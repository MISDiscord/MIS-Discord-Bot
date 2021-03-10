
def seconds_to_age(seconds: int):
    if type(seconds) != int:
        return None
    return_string = ""
    years = divmod(seconds, 31556926)[0]
    new_seconds = seconds - (31556926 * years)
    months = divmod(new_seconds, 2629743)[0]
    new_seconds = new_seconds - (2629743 * months)
    weeks = divmod(new_seconds, 604800)[0]
    new_seconds = new_seconds - (604800 * weeks)
    days = divmod(new_seconds, 86400)[0]
    new_seconds = new_seconds - (86400 * days)
    hours = divmod(new_seconds, 3600)[0]
    new_seconds = new_seconds - (3600 * hours)
    minutes = divmod(new_seconds, 60)[0]
    time_array = {
        "Years": years,
        "Months": months,
        "Weeks": weeks,
        "Days": days,
        "Hours": hours,
        "Minutes": minutes
    }
    interval_array = list({interval: values for interval, values in time_array.items() if values != 0})[:3]
    for i in interval_array:
        return_string += f'{int(time_array[i])} {i}, '
    print(return_string[:-2])
    return return_string[:-2]


def find_invite_by_code(invite_list, code):
    print("Find invite by code test output ", invite_list, code)
    for inv in invite_list:
        print("Invite", inv)
        if str(inv.code) == str(code):
            return inv
    return None
