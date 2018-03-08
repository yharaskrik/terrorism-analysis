import operator


class Filter:

    # Filter out the data that we do not want
    def filter(self, data, year=None, region=None):
        print('Filtering on: ', year, ' and ', region)
        data = data[(data.gname != None) & (data.city != None) & (data.gname != 'Unknown') & (data.city != 'Unknown')]

        if year:
            data = data.loc[(data['iyear'] >= year)]
        if region:
            data = data[data['region'].isin(region)]
        return data

    # Only include dictionary entries that we want to keep
    # Also removes Centralities of 0.0
    def filter_dict(self, d, keys):
        print('Filtering')
        return {key: d[key] for key in keys if key in d and d[key] != 0.0}

    # Sort a dictionary and return a list of sorted tuples
    def sort_dict(self, data):
        print('Sorting')
        return sorted([(key, data[key]) for key in data], key=operator.itemgetter(1), reverse=True)

    # Sort a list of tupples
    def sort_list(self, data):
        print('Sorting')
        return sorted(data, key=operator.itemgetter(1), reverse=True)
