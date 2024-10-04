from datetime import datetime

def get_formatted_date():
    # Get today's date
    today = datetime.today()
    
    # Format date as '12 March 2024'
    formatted_date = today.strftime('%d %B %Y')
    
    return formatted_date

def main():
    print("Today:", get_formatted_date())

if __name__=="__main__":
    main()
