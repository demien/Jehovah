@staticmethod
def count_user():
    command = \
        "awk 'BEGIN{FS=","}{if(!($1 in d)){d[$1] = 1}}END{for(i in d){n++} print n}' t_alibaba_data.csv"