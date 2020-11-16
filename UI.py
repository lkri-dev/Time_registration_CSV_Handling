from datasetOperations import Dataset
from registrationObj import RegistrationObj
import datetimeTool

csv_files = 'Eksport20200101-20201101.csv', 'Eksport20190101-20191231.csv'  #csv file to be analysed
weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']                #name of weekdays for print outs


"""Control switch"""
def switch(control, registrations):
    if control == '1':
        empty_days = registrations.find_empty_workdays()
        print(empty_days[0])

    elif control == '2':
        under_worked_days = registrations.find_under_worked_days()
        for d in under_worked_days:
            print('{}\t{}\t{}'.format(d[0], weekdays[d[0].weekday()], d[1]))

    elif control == '3':
        result = registrations.clean_data_set_for_duplicates()
        registrations.print_duplicates_list()
        return result

    elif control == '4':
        print(registrations.get_stat_of_workeddays())

    else:
        print('none')


"""Main function"""
def main():
    for file in csv_files:
        registrations = Dataset(file)
        #registrations.print_registration_dataset()

        switch('3', registrations)
        switch('4', registrations)


if __name__ == '__main__':
    main()

