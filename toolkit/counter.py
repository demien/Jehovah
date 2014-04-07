@staticmethod
def count_user(file_path='../data_resource/t_alibaba_data.csv'):
    command = \
        "awk 'BEGIN{FS=","}{if(!($1 in d)){d[$1] = 1}}END{for(i in d){n++} print n}' %s" % file_path