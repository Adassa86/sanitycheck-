from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import os
from django.contrib  import messages
import pandas as pd
import datetime
from datetime import datetime as td


def home(request):

    if request.method == 'POST':
        uploaded_file = request.FILES['uploaded_file']
        uploaded_file2 = request.FILES[' uploaded_file2']
        print(uploaded_file)
        print(uploaded_file2)

        listing_loc = uploaded_file
        names_loc = uploaded_file2

        results_list = []

        listing_file = pd.read_excel(listing_loc, index_col=None)

        if not 'Test ID' in listing_file.keys():
            results_list.append('WARNING: The column \'Test ID\' is not in the original file')
            print('WARNING: The column \'Test ID\' is not in the original file')

        headers = ['Vector Name', 'Date and Time', 'Test ID', 'PCR POS/Neg']
        output_df = pd.DataFrame(columns=headers)

        with open(names_loc) as fp:
            for line in fp.readlines():
                line = line.rstrip("\\\n")
                full_name = line.split(',')
                sample_name = full_name[0].split('_mean')
                try:
                    if len(sample_name[0].split('SCO_')) > 1:
                        sample_id = int(sample_name[0].split('SCO_')[1])
                    else:
                        sample_id = int(sample_name[0].split('SCO')[1])
                except:
                    sample_id = sample_name[0]

                try:
                    if listing_file['Test ID'].isin([sample_id]).any():
                        line_data = listing_file.loc[listing_file['Test ID'].isin([sample_id])]

                        vector_name = line

                        d_t = full_name[1].split('us_')[1].split('_')
                        date_time = td(int(d_t[0]), int(d_t[1]), int(d_t[2]), int(d_t[3]), int(d_t[4]), int(d_t[5]))
                        #                 print(date_time)

                        date_index = list(line_data['Collecting  Date from the subject'].iteritems())

                        for x in date_index:
                            if type(x[1]) is str():
                                date_time_obj = td.strptime(x[1], '%Y.%m.%d.  %H:%M')
                            elif type(x[1]) is pd.Timestamp:
                                date_time_obj = x[1]
                            elif type(x[1]) is datetime.datetime:
                                date_time_obj = x[1]

                        frame_time = str(date_time - date_time_obj)

                        if date_time - date_time_obj > datetime.timedelta(hours=48):
                            results_list.append('WARNING: The time frame is over 48 ({}) for sample {}'.format(
                                date_time - date_time_obj, sample_id))

                            print('WARNING: The time frame is over 48 ({}) for sample {}'.format(
                                date_time - date_time_obj, sample_id))

                        test_id = sample_id

                        pcr_index = list(line_data['PCR Pos/Neg'].iteritems())
                        if len(pcr_index) > 1:
                            results_list.append(
                                'Warning: Sample {} Has more than one attribute in the listing file'.format(sample_id))
                            print(
                                'Warning: Sample {} Has more than one attribute in the listing file'.format(sample_id))
                        for x in pcr_index:
                            pcr_ans = x[1].strip()

                        values_to_add = {'Vector Name': vector_name,
                                         'Date and Time': date_time,
                                         'Test ID': test_id,
                                         'PCR POS/Neg': pcr_ans,
                                         'Time Frame': frame_time
                                         }

                        row_to_add = pd.Series(values_to_add)
                        output_df = output_df.append(row_to_add, ignore_index=True)
                    else:
                        results_list.append('Warning: Sample {} not in the listing file'.format(sample_name[0]))
                        print('Warning: Sample {} not in the listing file'.format(sample_name[0]))
                except:
                    results_list.append('The Template name is not good: {}'.format(sample_id))
                    print('The Template name isnt good: {}'.format(sample_id))

            print(results_list)

        if uploaded_file.name.endswith('.xls'):
             # save the file in media folder
            savefile = FileSystemStorage()

            file = savefile.save(uploaded_file.name, uploaded_file)
            file2 = savefile.save(uploaded_file2.name, uploaded_file2)
            d = os.getcwd()
            file_directory = d+'/media/' + file
            file_directory2 = d+'/media/' + file2

            readfile(file_directory)
            readfile(file_directory2)
            context={
                "results": results_list
            }
            return render(request,"results.html",context)

        else:
            messages.warning(request,'File was not uploaded , please use xls file extension ')

    return render(request, "index.html")


def readfile(filename):

    my_file = pd.read_excel(uploaded_file, index_col=None)

    data= pd.Dataframe(data=my_file,index=None)
    print(data)

def results(request):
    return render(request, 'results.html')

