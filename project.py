from tabulate import tabulate
from pyfiglet import Figlet
import datetime
import re
import sys

figlet = Figlet()
figlet.setFont(font="nancyj-underlined")

global today
today = datetime.date.today()

global today_dd
global today_mm
global today_yyyy
today_dd, today_mm, today_yyyy = (today.strftime("%d %m %Y")).split(" ")
today_dd = int(today_dd)
today_mm = int(today_mm)
today_yyyy = int(today_yyyy)


def main():
    print(
        "Welcome to my fixed-rate mortgage calculator.\nIt helps you to calculate your monthly mortgage payment based on your desired amortization period.\n15-year and 30-year mortgages are the most popular types of mortgages.\nHowever, you can choose any amortization period you like."
    )
    # Getting the home's purchase price hpp
    while True:
        try:
            hpp = int(input("Purchase price in $: "))
            if hpp < 0:
                raise ValueError
        except ValueError:
            print("Please enter a whole number greater than zero.")
        else:
            break

    # Getting the down payment dp
    while True:
        try:
            dp = int(input("Down payment in $: "))
            min_dp = round(hpp / 5)
            if dp < min_dp:
                raise ValueError
            elif hpp - dp < 0:
                raise ValueError

        except ValueError:
            print(
                f"Please enter a whole number. Your down payment must be at least 20% of the home's purchase price, that is ${min_dp:,.0f}."
            )
        else:
            break

    # Calculating the principal p
    p = hpp - dp

    # Getting the annual interest rate i in percent
    while True:
        try:
            i = float(input("Interest rate in %: "))
            if i < 0:
                raise ValueError
        except ValueError:
            print(
                "Please enter a number greater than zero with no more than two decimal places, e.g 5.25."
            )
        else:
            break

    # Getting the amortization period t in years
    while True:
        try:
            t = int(input("Desired amortization period in years: "))
            if t < 1:
                raise ValueError
        except ValueError:
            print("Please enter a whole number greater than zero.")
        else:
            break

    # Getting the mortgage start date
    while True:
        try:
            start_date = input("Mortgage start date(mm/yyyy): ").strip()
            if not re.search(r"^(0[1-9]|1[0-2])\/\d{4}$", start_date):
                raise ValueError
            else:
                global mm
                global yyyy
                mm, yyyy = start_date.split("/")
                mm = int(mm)
                yyyy = int(yyyy)
                start_date = datetime.date(yyyy, mm, today_dd)

            if start_date < today:
                raise ValueError

        except ValueError:
            print(
                f"Use the following date format: mm/yyyy (e.g. 0/2024). The earliest valid date is {today_mm:02d}/{today_yyyy}."
            )
        else:
            print("")
            break

    # Calculating the monthly interest rate mr
    mr = (i / 100) / 12

    # Calculating the number of payments n over the mortgage's lifetime (= number of months)
    global n
    n = t * 12

    monthly_payments = calculate_monthly_payments(p, mr, n)
    total_payment = calculate_total_payment(n, m)
    m_rates, y_rates, y_interest, tipping_point = calculate_rates(p, m, mr, n, mm, yyyy)

    print(figlet.renderText("Your Mortgage Payment Plan"))
    print(f"Your mortgage amount is §\033[1m{p:,.2f}\033[0m.\n")
    print(f"Your monthly payment is $\033[1m{monthly_payments:,.2f}\033[0m.\n")
    print(
        f"The number of payments over a \033[1m{t}-year\033[0m period is \033[1m{n}\033[0m.\n"
    )
    print(
        f"Your total payment over a \033[1m{t}-year\033[0m period is $\033[1m{total_payment:,.2f}\033[0m.\n"
    )
    print(
        f"Your total interest over a \033[1m{t}-year\033[0m period is $\033[1m{y_interest:,.2f}\033[0m.\n"
    )

    # Calculating the interest-to-principal ratio ipr in percent
    ipr = (y_interest / p) * 100
    print(f"The interest-to-principal ratio is \033[1m{ipr:.2f}%\033[0m\n")

    # Printing the tipping point
    print(f"The tipping point is reached in \033[1m{tipping_point}\033[0m\n")

    # Asking users if they want a monthly and annual breakdown of their mortgage payment schedule
    while True:
        user_input = input(
            "Are you interested in a detailed (monthly and annual) breakdown of your mortgage payment schedule (y/n)? "
        )
        yes_choices = ["yes", "y"]
        no_choices = ["no", "n"]
        if user_input.lower() in yes_choices:
            print()
            print("\033[1mYour monthly payment schedule\033[0m")

            # Printing two tables with the payment schedules per month and per year
            print(
                tabulate(
                    m_rates,
                    headers="keys",
                    numalign="decimal",
                    tablefmt="mixed_grid",
                    floatfmt=",.2f",
                )
            )

            print()
            print("\033[1mYour annual payments\033[0m")

            print(
                tabulate(
                    y_rates,
                    headers="keys",
                    numalign="decimal",
                    tablefmt="mixed_grid",
                    floatfmt=",.2f",
                )
            )

            print()
            sys.exit(
                "Thank your for your interest in my mortgage amortization calculator.\n"
            )

        elif user_input.lower() in no_choices:
            print()
            sys.exit(
                "Thank your for your interest in my mortgage amortization calculator.\n"
            )

        else:
            print()
            print("You may enter either 'y'/'yes' or 'n'/'no'.\n")


# Calculating the monthly rate
def calculate_monthly_payments(p, mr, n):
    global m
    m = round(p * ((mr * (1 + mr) ** n)) / ((1 + mr) ** n - 1), 2)
    return m


# Calculating the total payment over the entire amortization period
def calculate_total_payment(n, m):
    global tp
    tp = round(m * n, 2)
    return tp


def calculate_rates(p, m, mr, n, mm, yyyy):
    # Dictionary for monthly payments, i.e. monthly payment, monthly interest and monthly repayment of the principal
    global m_dict
    m_dict = {
        "Month/Year": [],
        "Total Payment": [],
        "Payment Towards Interest": [],
        "Payment Towards Principal": [],
        "Remaining Balance": [],
    }

    # Dictionary for annual payments, i.e. annual payment, annual interest and annual repayment of the prinicipal
    y_dict = {
        "Year": [],
        "Total Payment": [],
        "Payment Towards Interest": [],
        "Payment Towards Principal": [],
        "Remaining Balance": [],
    }

    sum_m_interest = 0
    sum_m_principal = 0

    # start_principal = the money borrowed from the bank (home value - down payment)
    start_principal = p
    y_m = 0
    y_interest = 0
    y_principal = 0
    tipping_point_counter = 0

    for _ in range(n):
        mm_yyyy = date(mm, yyyy)
        m_interest = p * mr
        m_principal = m - m_interest
        p -= m_principal

        # Aggregating monthly interest and principal throughout the mortgage's lifetime.
        sum_m_interest += m_interest
        sum_m_principal += m_principal
        remaining_principal = start_principal - sum_m_principal

        # Correcting accumulated rounding errors in the final run of the loop
        if _ == n - 1 and remaining_principal > 0:
            # Correcting rounding errors in the MONTHLY dict
            rounding_error = round(abs(remaining_principal), 2)
            m -= rounding_error
            m_principal -= rounding_error

            # Correcting the rounding error in the ANNUAL dict
            y_m -= rounding_error
            y_principal -= rounding_error

            p = 0
            remaining_principal = 0

        elif _ == n - 1 and remaining_principal < 0:
            # Correcting the error in the monthly dict
            rounding_error = round(abs(remaining_principal), 2)
            m += rounding_error
            m_principal += rounding_error

            # Correcting the rounding error in the ANNUAL dict
            y_m += rounding_error
            y_principal += rounding_error

            p = 0
            remaining_principal = 0

        m_dict["Month/Year"].append(mm_yyyy)
        m_dict["Total Payment"].append("{:.2f}".format(m))
        m_dict["Payment Towards Interest"].append("{:.2f}".format(m_interest))
        m_dict["Payment Towards Principal"].append("{:.2f}".format(m_principal))
        m_dict["Remaining Balance"].append("{:.2f}".format(p))

        # Calculating the tipping point
        diff_tipping_point = m_interest - m_principal

        if tipping_point_counter == 0 and diff_tipping_point < 0:
            tipping_point = mm_yyyy
            tipping_point_counter += 1
        else:
            pass

        # Aggregating monthly rate m, monthly interest and monthly principal over a period of one calendar(!) year
        y_m += m
        y_interest += m_interest
        y_principal += m_principal

        # Using modulo 12 to find the last month of each calendar year and appending the values aggregated over a calendar year to the dict that holds the annual values
        if (mm % 12) == 0:
            y_dict["Year"].append(yyyy)
            y_dict["Total Payment"].append("{:.2f}".format(y_m))
            y_dict["Payment Towards Interest"].append("{:.2f}".format(y_interest))
            y_dict["Payment Towards Principal"].append("{:.2f}".format(y_principal))
            y_dict["Remaining Balance"].append("{:.2f}".format(remaining_principal))

            # Resetting annual values and the month to zero
            y_m = 0
            y_interest = 0
            y_principal = 0
            mm = 0

            # Incrementing the variable holding the value for the year
            yyyy += 1

        # Appending the values of the final year to the annual dict
        elif _ == n - 1:
            y_dict["Year"].append(yyyy)
            y_dict["Total Payment"].append("{:.2f}".format(y_m))
            y_dict["Payment Towards Interest"].append("{:.2f}".format(y_interest))
            y_dict["Payment Towards Principal"].append("{:.2f}".format(y_principal))
            y_dict["Remaining Balance"].append("{:.2f}".format(remaining_principal))

        mm += 1

    return m_dict, y_dict, round(sum_m_interest, 2), tipping_point


# Dictionary to create a column in the monthly payment table that contains the name of the months as nouns and
# not as numbers from 1 to 12
def date(mm, yyyy):
    months_dict = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "Oktober",
        "11": "November",
        "12": "December",
    }

    for key in months_dict:
        if int(key) == mm:
            month = months_dict[key]
            return f"{month} {yyyy}"


if __name__ == "__main__":
    main()
