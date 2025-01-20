from datetime import datetime

def get_formatted_date():
    # Get today's date
    today = datetime.today()
    
    # Format date as '12 March 2024'
    formatted_date = today.strftime('%d %B %Y')
    
    return formatted_date

def parse_values_bytype(atype, astr):
    """parse three type of inputs
        single value
        a list of values: ","
        a range: start:stop:step
    """

    if ":" in astr:
        start, stop, step = map(int, astr.split(":"))
        alist = list(range(start,stop,step))
        if not stop in alist:
            alist.append(stop)
        alist = map(str, alist)
        alist = list(alist)
    elif "," in astr:
        alist = astr.split(",")
    else:
        alist = [astr]
    
    return alist

def main():
    print("Today:", get_formatted_date())

if __name__=="__main__":
    main()
