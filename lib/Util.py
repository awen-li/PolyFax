

import copy 
import csv 
import sys
import statistics 
from itertools import combinations 
from collections import Counter
from collections import OrderedDict
from progressbar import * 


csv.field_size_limit(sys.maxsize)

class Util:
    Server_Num = 201

    @staticmethod
    def create_dictionary(keys, values):
        return {k: v for (k, v) in zip(keys, values)}

    @staticmethod
    def combine_dictionaries(dict1, dict2):
        return dict(Counter(dict1) + Counter(dict2))

    @staticmethod
    def sort_dictionary_into_list(dictionary, sortByMaxValue):
        return list(sorted(dictionary, key=dictionary.__getitem__, reverse=sortByMaxValue))

    @staticmethod
    def sort_list(array, sortByMaxValue):
        return list(sorted(array, reverse=sortByMaxValue))

    @staticmethod
    def jsonString_to_object(json_string):
        import ast 
        value = ''
        try:
            value = ast.literal_eval(json_string)
        except SyntaxError:
            value = json_string
        except ValueError:
            value = json_string
        return value

    @staticmethod
    def calculate_top_dict_key(dictionary, exclude_key):
        deep_copy = copy.deepcopy(dictionary)
        if (exclude_key != None) and (exclude_key in deep_copy):
            deep_copy.pop(exclude_key)
        max_key = ''
        if len(deep_copy) != 0:
            max_key = max(deep_copy, key=deep_copy.get)
        return max_key

    @staticmethod
    def calculate_stats(array):
        stat_dict = {'sum': 0, 'avg': 0, 'median': 0, 'std': 0, 'var': 0}
        stat_dict['sum'] = sum(array)
        if len(array) >= 2:
            stat_dict['avg']    = round(statistics.mean(array), 4)
            stat_dict['median'] = round(statistics.median(array), 4)
            stat_dict['std']    = round(statistics.stdev(array), 4)
            stat_dict['var']    = round(statistics.variance(array), 4)
        else:
            stat_dict['avg']    = array[0]
            stat_dict['median'] = array[0]
            stat_dict['std']    = array[0]
            stat_dict['var']    = array[0]
        return stat_dict

    @staticmethod
    def create_unique_combo_list(languages, dict_count, max_combo_count, min_combo_count=1):
        combos = []
        items = languages
        if dict_count < min_combo_count or dict_count > max_combo_count:
            return combos
        for i in range(min_combo_count, dict_count + 1, 1):
            sub_combo = [list(x) for x in combinations(items, i)]#combinations_with_replacement
            if len(sub_combo) > 0:
                combos.extend(sub_combo)
        return combos

    @staticmethod
    def check_if_path_exist(file):
        # Checks if a path to file exist
        from pathlib import Path
        file_path = Path(file)
        if file_path.is_file() == False:
            error = "No such path to file: '" + file + "'"
            sys.exit(error)


    @staticmethod
    def named_tuple_format(key_list):
        # Creates the field names for our python object from csv header row fields
        tuple_format = {}
        for index in range(0, len(key_list), 1):
            key = key_list[index].replace(" ", "_").lower()
            # key is index of the column and value is the column name
            tuple_format[index] = key  # i.e. {1: 'name', 2: 'id'}
        return tuple_format


    @staticmethod
    # This function reads in all the rows of a csv file and prepares them for processing
    def read_in_data(file_path, file_name, class_name):
        file_name = file_path + file_name + '.csv'
        Util.check_if_path_exist(file=file_name)
        list_of_objects = []
        # Opens the CSV file for reading
        with open(file_name, 'r') as csv_file:
            reader = csv.reader(csv_file)
            is_header_row = True
            tuple_format = {}
            # Every row is a unique item
            pbar = ProgressBar()
            for row in pbar(list(reader)):
                # The first row of the CSV file contains all the column names/headers
                if is_header_row:
                    is_header_row = False  # We only want to execute this conditional once
                    # Creates the field names for our python object from csv header row fields
                    tuple_format = Util.named_tuple_format(row)
                    continue
                # Formats the row's fields into their correct type
                for index in range(0, len(row), 1):
                    row[index] = Util.jsonString_to_object(row[index])
                # This line converts the row into an python objects
                new_object = Util.convert_to_named_tuple(class_name=class_name, dictionary=tuple_format, values=row)
                list_of_objects.append(new_object)
        return list_of_objects

    @staticmethod
    def convert_to_named_tuple(class_name, dictionary, values):
        # Converts a dictionary into a class (tuple)
        from collections import namedtuple  # namedtuple()
        return namedtuple(class_name, dictionary.values())(*values)

    @staticmethod
    def percentile_partition_dictionary(dictionary, upper_percent, lower_percent):
        import numpy as np
        results = {}
        values = np.array([float(x) for x in dictionary.values()])
        upper_limit = np.percentile(values, upper_percent, interpolation='higher')
        lower_limit = np.percentile(values, lower_percent, interpolation='lower')
        for key, value in dictionary.items():
            if upper_limit >= value >= lower_limit:
                results[key] = value
        if len(results) > 100:
            print("Error: Too many results within percentiles specified.")
            return {}
        return results

    @staticmethod
    def store_data(file_path, file_name, data):
        # Saves objects to be loaded at a later time
        import pickle
        # Its important to use binary mode
        file = file_path + file_name
        # Opens to write binary
        pickle_file = open(file, 'wb')
        # source, destination
        pickle.dump(data, pickle_file)
        pickle_file.close()

    @staticmethod
    def load_data(file_path, file_name):
        # Saves objects to be loaded at a later time
        import pickle
        # Its important to use binary mode
        file = file_path + file_name
        # Opens to write binary
        pickle_file = open(file, 'rb')
        # source, destination
        data = pickle.load(file=pickle_file)
        pickle_file.close()
        return data

    @staticmethod
    def dict_to_list(dict):
        list = []
        for item in dict:
            list.append(dict[item])
        return list

    @staticmethod
    def dictsort_value(original_dict, reverse=False):
        items = sorted(original_dict.items(), key=lambda obj: obj[1], reverse=reverse)

        new_dict = {}
        for item in items:
            new_dict[item[0]] = original_dict[item[0]]
        return new_dict

    @staticmethod
    def dictsort_key(original_dict, reverse=False):
        new_dict = {}
        for key in sorted(original_dict):
            new_dict[key] = original_dict[key]
        return new_dict

    
