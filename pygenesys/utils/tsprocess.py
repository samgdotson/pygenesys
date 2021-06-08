import numpy as np
import pandas as pd


def choose_distribution_method(N_seasons, N_hours):
    """
    This function returns a function that appropriately calculates
    the distribution based on the specified time slices. In the
    future, there may be a way to make this more generic.

    Parameters
    ----------
    data_path : string
        The path to the data. Should be a .csv file
    N_seasons : integer
        The number of seasons in the energy system model.
    N_hours : integer
        The hourly resolution of the energy system model.

    Returns
    -------
    distribution_func : function
        The function to generate a specific distribution of data.
    """
    distribution_func = None

    if (N_seasons is 4) and (N_hours is 24):
        distribution_func = four_seasons_hourly

    return distribution_func



def four_seasons_hourly(data_path, N_seasons=4, N_hours=24):
    """
    This function calculates a seasonal trend based on the
    input data. Answers the question: what fraction of the annual
    demand is consumed at this time of the year?

    Parameters
    ----------
    data_path : string
        The path to the time series data
            * must be a ``.csv`` file.
            * nust have a column ``time`` that is a pandas datetime column.
        Tips:
            * Sometimes a dataset will have an index column that can
              be read as an ``Unnamed Column: 0``. If a user supplies
              their own data, this should be removed where applicable.

    N_seasons : integer
        The number of seasons in the energy system model.
    N_hours : integer
        The hourly resolution of the energy system model.

    Returns
    -------
    distribution : numpy array
        The time series data distributed over the specified time
        slices.
    """
    time_series = pd.read_csv(data_path,
                              usecols = [0,1],
                              index_col=['time'],
                              parse_dates=True,
                             )

    if N_seasons is 4:
        spring_mask = ((time_series.index.month >= 3) &
                       (time_series.index.month <= 5))
        summer_mask = ((time_series.index.month >= 6) &
                       (time_series.index.month <= 8))
        fall_mask = ((time_series.index.month >= 9) &
                     (time_series.index.month <= 11))
        winter_mask = ((time_series.index.month == 12) |
                       (time_series.index.month == 1) |
                       (time_series.index.month == 2))

        seasons = {'spring':spring_mask,
                   'summer':summer_mask,
                   'fall':fall_mask,
                   'winter':winter_mask}

    # initialize dictionary
    seasonal_hourly_profile = np.zeros(N_seasons*N_hours)
    print(seasonal_hourly_profile)
    for i, season in enumerate(seasons):
        mask = seasons[season]
        season_df = time_series[mask]
        hours_grouped = season_df.groupby(season_df.index.hour)

        avg_hourly = np.zeros(len(hours_grouped))
        std_hourly = np.zeros(len(hours_grouped))
        for j, hour in enumerate(hours_grouped.groups):
            hour_data = hours_grouped.get_group(hour)
            avg_hourly[j] = hour_data.iloc[1].mean()
            std_hourly[j] = hour_data.iloc[1].std()
            # print(hour_data.head(24))
            print(hour_data.iloc[1,:])


        data = (avg_hourly/(N_seasons*avg_hourly.sum()))
        seasonal_hourly_profile[i*N_hours:(i+1)*N_hours] = data



    print(time_series.head())

    return seasonal_hourly_profile


if __name__ == '__main__':

    from pygenesys.data.library import campus_elc_demand
    import matplotlib.pyplot as plt
    plt.style.use('ggplot')

    # df = pd.read_csv(campus_elc_demand, index_col='time', parse_dates=True, usecols=['time', 'kw'])
    # df.plot()
    # plt.show()

    seasons={0:'spring',
             1:'summer',
             2:'fall',
             3:'winter'}

    N_seasons = 4
    N_hours = 24
    method = choose_distribution_method(N_seasons, N_hours)
    profile = method(campus_elc_demand)
    print(profile.sum())
    for i in range(N_seasons):
        plt.plot(range(N_hours),
                 profile[i*N_hours:(i+1)*N_hours],
                 label=f'{seasons[i].capitalize()}',
                 marker='.')
    plt.legend()
    plt.show()
