"""Wrapper for simple_wbd api.

This wrapper adds extra functionality to the IndicatorDataset class, for easier
data manipulation and generating Orange data tables.
"""

import datetime
import time
import logging

import numpy as np

import Orange
import simple_wbd
from orangecontrib.datasets import countries

logger = logging.getLogger(__name__)


class IndicatorDataset(simple_wbd.IndicatorDataset):
    """Extended indicator dataset.

    This class extends the original indicator dataset by adding as_np_array and
    as_orange_table functions.
    """


    @staticmethod
    def _get_iso_date(date_str):
        """Convert wbd date string into iso format date string.

        Convert date strings such as "2005", "2002Q3" and "1999M7" into iso
        formatted date strings "yyyy-mm-dd"
        """
        try:
            if "Q" in date_str:
                year, quarter = date_str.split("Q")
                return datetime.date(int(year), (int(quarter) * 3) - 2, 1)
            elif "M" in date_str:
                year, month = date_str.split("M")
                return datetime.date(int(year), int(month), 1)
            else:
                return datetime.date(int(date_str), 1, 1).isoformat()
        except ValueError:
            # some dates contain invalid date strings such as
            # "Last Known Value" or "1988-2000" and possible some more. See:
            # http://api.worldbank.org/countries/PRY/indicators/
            #   per_lm_ac.avt_q4_urb?date=1960%3A2016&format=json
            #   &per_page=10000
            # http://api.worldbank.org/countries/all/indicators/
            #   DB_mw_19apprentice?format=json&mrv=10&gapfill=y
            return datetime.date.today().isoformat()

    def _time_series_table(self):
        data = self.as_np_array(time_series=True)

        if not data.any():
            return None

        meta_columns = [[time.mktime(date_.timetuple()) if date_ else None]
                        for date_ in data[1:, 0]]
        data_columns = data[1:, 1:]

        meta_domains = [Orange.data.TimeVariable("Date")]

        colum_domains = [Orange.data.ContinuousVariable(column_name)
                         for column_name in data[0, 1:]]

        logger.debug("Generated Orange table of size: %s", data.shape)

        domain = Orange.data.Domain(colum_domains, metas=meta_domains)
        return Orange.data.Table(domain, data_columns, metas=meta_columns)

    def _country_table(self):

        def nonesorter(a):
            if not a:
                return ""
            return a

        data = self.as_np_array(add_metadata=True)

        if not data.any():
            return None

        meta_columns = data[1:, :7]

        data_columns = data[1:, 7:]
        regions = {r: i for i, r in enumerate(sorted(set(meta_columns[:, 1]), key=nonesorter))}
        admin_regions = {r: i for i, r in enumerate(sorted(set(meta_columns[:, 2]), key=nonesorter))}
        income_level = {r: i for i, r in enumerate(sorted(set(meta_columns[:, 3]), key=nonesorter))}
        lending_type = {r: i for i, r in enumerate(sorted(set(meta_columns[:, 6]), key=nonesorter))}

        meta_domains = [
          Orange.data.StringVariable("Country"),
          Orange.data.DiscreteVariable(
            "Region",
            values=sorted(regions.keys(), key=nonesorter)
          ),
          Orange.data.DiscreteVariable(
            "Admin region",
            values=sorted(admin_regions.keys(), key=nonesorter)
          ),
          Orange.data.DiscreteVariable(
            "Income level",
            values=sorted(income_level.keys(), key=nonesorter)
          ),
          Orange.data.ContinuousVariable("Longitude"),
          Orange.data.ContinuousVariable("Latitude"),
          Orange.data.DiscreteVariable(
            "Lending type",
            values=sorted(lending_type.keys(), key=nonesorter)
          ),
        ]
        column_domains = [Orange.data.ContinuousVariable(column_name)
                         for column_name in data[0, 7:]]
        for row in meta_columns:
          row[1] = regions[row[1]]
          row[2] = admin_regions[row[2]]
          row[3] = income_level[row[3]]
          row[6] = lending_type[row[6]]

        logger.debug("Generated Orange table of size: %s", data.shape)

        domain = Orange.data.Domain(column_domains, metas=meta_domains)

        data_columns = data_columns.astype(float)
        data_columns = np.where(data_columns == np.array(None), np.nan, data_columns)
        data_columns = np.where(data_columns == '', np.nan, data_columns)
        meta_columns = np.where(meta_columns == np.array(None), np.nan, meta_columns)
        meta_columns = np.where(meta_columns == '', np.nan, meta_columns)
        for row in meta_columns[:, 1:]:
            row[3] = float(row[3])
            row[4] = float(row[4])

        return Orange.data.Table(domain, data_columns, metas=meta_columns)

    def as_np_array(self, time_series=False, add_metadata=False, **kwargs):
        """Get a 2D numpy array data representation.

        Args:
            time_series: boolean indicating if the first column should contain
                countries or dates. Different indicators are always in columns
                so this is not a transposition of the matrix.
            add_metadata: This can only be used if time_series is false. If
                set to True, it will append country metadata after the first
                column. Columns added: Region, Admin Region, Income Level,
                latitude, longitude, and Lending type.

        Returns:
            2D numpy array with all indicator data.
        """
        data = np.array(self.as_list(time_series=time_series,
                                        add_metadata=add_metadata,
                                        **kwargs))

        # list of column indexes that have at least one non zero value
        filter_ = [ind for ind, col in enumerate(data[1:, :].T) if any(col)]
        return data[:, filter_]

    def as_orange_table(self, time_series=False):
        if time_series:
            return self._time_series_table()
        else:
            return self._country_table()


class IndicatorAPI(simple_wbd.IndicatorAPI):
    """Wrapper for Indicator API to use the extended data set."""

    def __init__(self):
        super().__init__(IndicatorDataset)


class ClimateDataset(simple_wbd.ClimateDataset):
    """Extended climate dataset.

    This class extends the original climate dataset by adding as_np_array and
    as_orange_table functions.
    """


    def as_np_array(self, **kwargs):
        """Get a 2D numpy array data representation.

        Returns:
            2D numpy array with all indicator data.
        """
        data = np.array(self.as_list(**kwargs))

        # list of column indexes that have at least one non zero value
        filter_ = [ind for ind, col in enumerate(data[1:, :].T) if any(col)]
        return data[:, filter_]

    def _country_table(self, **kwargs):
        data = self.as_np_array(**kwargs)
        if data.shape[0] < 2:
            return None
        alpha3_map = countries.get_alpha3_map()
        meta_columns = data[1:, :1]
        data_columns = data[1:, 1:]
        for row in meta_columns:
            row[0] = alpha3_map.get(row[0], row[0])

        meta_domains = [Orange.data.StringVariable(name)
                        for name in data[0, :1]]
        colum_domains = [Orange.data.ContinuousVariable(column_name)
                         for column_name in data[0, 1:]]

        logger.debug("Generated Orange table of size: %s", data.shape)

        domain = Orange.data.Domain(colum_domains, metas=meta_domains)
        return Orange.data.Table(domain, data_columns, metas=meta_columns)

    def _time_series_table(self, **kwargs):
        data = self.as_np_array(columns=["country", "type"], use_dates=True,
                                **kwargs)
        if data.shape[0] < 2:
            return None
        alpha3_map = countries.get_alpha3_map()
        meta_columns = [[time.mktime(date_.timetuple()) if date_ else None]
                        for date_ in data[1:, 0]]
        data_columns = data[1:, 1:]
        for row in meta_columns:
            row[0] = alpha3_map.get(row[0], row[0])

        meta_domains = [Orange.data.TimeVariable(name)
                        for name in data[0, :1]]
        colum_domains = [Orange.data.ContinuousVariable(column_name)
                         for column_name in data[0, 1:]]

        logger.debug("Generated Orange table of size: %s", data.shape)

        domain = Orange.data.Domain(colum_domains, metas=meta_domains)
        return Orange.data.Table(domain, data_columns, metas=meta_columns)

    def as_orange_table(self, time_series=False, **kwargs):
        if time_series:
            return self._time_series_table(**kwargs)
        else:
            return self._country_table(**kwargs)


class ClimateAPI(simple_wbd.ClimateAPI):
    """Wrapper for Climate API to use the extended data set."""
    # pylint: disable=too-few-public-methods
    # This is just an extension of the returned dataset. We do not need to add
    # any additional functions here.

    def __init__(self):
        super().__init__(ClimateDataset)
