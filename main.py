"""
Simulation of Online Shop Call Center

Author: Ehsan Cheshomi
Date: 1401 / 3 / 25
"""

import random
import math
import pandas as pd


random.seed(143)


def starting_state():

    # Simulation parameters
    parameters = dict()
    parameters["Number of Normal Operators"] = 3
    parameters["Number of Expert Operators"] = 2
    parameters["Number of Technical Operators"] = 2

    # State variables
    state = dict()
    state['Normal QL'] = 0
    state['VIP QL'] = 0
    state['Normal Technical QL'] = 0
    state['VIP Technical QL'] = 0
    state['Normal Call-back QL'] = 0
    state['VIP Call-back QL'] = 0
    state['Expert Operators Serving'] = 0
    state['Normal Operators Serving'] = 0
    state['Technical Operators Serving'] = 0
    state['Shift'] = 1
    state['Day'] = 1
    state['Disruption'] = 0
    state['Disruption Day'] = 0

# Data: will save everything
    data = dict()

    data['Customers'] = dict()  # To track each customer, saving their arrival time, time service begins, etc.

    data['Last Time QL Changed'] = dict()  # Needed to calculate area under queue length curve
    data['Last Time QL Changed']['Normal Q'] = 0
    data['Last Time QL Changed']['VIP Q'] = 0
    data['Last Time QL Changed']['Normal Technical Q'] = 0
    data['Last Time QL Changed']['VIP Technical Q'] = 0
    data['Last Time QL Changed']['Normal Call-back Q'] = 0
    data['Last Time QL Changed']['VIP Call-back Q'] = 0

    data['Queue Customers'] = dict()  # Customer: Arrival Time, used to find first customer in queue
    data['Queue Customers']['Normal Q'] = dict()
    data['Queue Customers']['VIP Q'] = dict()
    data['Queue Customers']['Normal Technical Q'] = dict()
    data['Queue Customers']['VIP Technical Q'] = dict()
    data['Queue Customers']['Normal Call-back Q'] = dict()
    data['Queue Customers']['VIP Call-back Q'] = dict()

    data['Maximum QL'] = dict()
    data['Maximum QL']['Normal Q'] = 0
    data['Maximum QL']['VIP Q'] = 0
    data['Maximum QL']['Normal Technical Q'] = 0
    data['Maximum QL']['VIP Technical Q'] = 0
    data['Maximum QL']['Normal Call-back Q'] = 0
    data['Maximum QL']['VIP Call-back Q'] = 0

    # Cumulative Stats
    data['Cumulative Stats'] = dict()

    data['Cumulative Stats']['Server Busy Time'] = dict()
    data['Cumulative Stats']['Server Busy Time']['Normal Operators'] = 0
    data['Cumulative Stats']['Server Busy Time']['Expert Operators'] = 0
    data['Cumulative Stats']['Server Busy Time']['Technical Operators'] = 0

    data['Cumulative Stats']['Queue Waiting Time'] = dict()
    data['Cumulative Stats']['Queue Waiting Time']['Normal Q'] = 0
    data['Cumulative Stats']['Queue Waiting Time']['VIP Q'] = 0
    data['Cumulative Stats']['Queue Waiting Time']['Normal Technical Q'] = 0
    data['Cumulative Stats']['Queue Waiting Time']['VIP Technical Q'] = 0
    data['Cumulative Stats']['Queue Waiting Time']['Normal Call-back Q'] = 0
    data['Cumulative Stats']['Queue Waiting Time']['VIP Call-back Q'] = 0

    data['Cumulative Stats']['Area Under QL Curve'] = dict()
    data['Cumulative Stats']['Area Under QL Curve']['Normal Q'] = 0
    data['Cumulative Stats']['Area Under QL Curve']['VIP Q'] = 0
    data['Cumulative Stats']['Area Under QL Curve']['Normal Technical Q'] = 0
    data['Cumulative Stats']['Area Under QL Curve']['VIP Technical Q'] = 0
    data['Cumulative Stats']['Area Under QL Curve']['Normal Call-back Q'] = 0
    data['Cumulative Stats']['Area Under QL Curve']['VIP Call-back Q'] = 0

    data['Cumulative Stats']['Service Starters'] = dict()
    data['Cumulative Stats']['Service Starters']['Normal Q'] = 0
    data['Cumulative Stats']['Service Starters']['VIP Q'] = 0
    data['Cumulative Stats']['Service Starters']['Normal Technical Q'] = 0
    data['Cumulative Stats']['Service Starters']['VIP Technical Q'] = 0
    data['Cumulative Stats']['Service Starters']['Normal Call-back Q'] = 0
    data['Cumulative Stats']['Service Starters']['VIP Call-back Q'] = 0

    data['Cumulative Stats']['Total Number of VIP Customers'] = 0
    data['Cumulative Stats']['Total Number of Normal Customers'] = 0
    data['Cumulative Stats']['Number of VIP Customers Not Using Call-back'] = 0
    data['Cumulative Stats']['Number of VIP Customers Not Waiting'] = 0
    data['Cumulative Stats']['Number of Normal Customers Served by Expert Operators'] = 0
    data['Cumulative Stats']['VIP Customers Total Time in System'] = 0

    # Starting FEL
    future_event_list = list()
    future_event_list.append({'Event Type': 'End of Month', 'Event Time': 0})
    future_event_list.append({'Event Type': 'Arrival', 'Event Time': 0.0001, 'Customer': 'C1'})
    # fel_maker(future_event_list, 'Arrival', 0)
    return state, future_event_list, data, parameters


def exponential(lambd):
    r = random.random()
    return -(1 / lambd) * math.log(r)


def uniform(a, b):
    r = random.random()
    return a + (b - a) * r


def is_VIP():
    r = random.random()
    if r < 0.3:
        return 'VIP'
    else:
        return 'Normal'


def use_callback():
    r = random.random()
    if r < 0.5:
        return 1
    else:
        return 0


def will_abandon():
    r = random.random()
    if r < 0.15:
        return 1
    else:
        return 0


def is_technical_needed():
    r = random.random()
    if r < 0.15:
        return 1
    else:
        return 0


def fel_maker(future_event_list, event_type, state, clock, customer=None, data=None):

    event_time = 0

    if event_type == 'Arrival':
        if state['Disruption']:
            if state['Shift'] == 1:
                event_time = clock + exponential(1 / 2)
            elif state['Shift'] == 2:
                event_time = clock + exponential(2)
            else:
                event_time = clock + exponential(1)
        else:
            if state['Shift'] == 1:
                event_time = clock + exponential(1 / 3)
            elif state['Shift'] == 2:
                event_time = clock + exponential(1 / 2)
            else:
                event_time = clock + exponential(1)

    elif event_type == 'Abandon':
        if data['Customers'][customer]['Type'] == 'VIP':
            x = max(25, state['VIP QL'])
        else:
            x = max(25, state['Normal QL'])
        event_time = clock + uniform(5, x)

    elif event_type == 'End of Expert Service':
        event_time = clock + exponential(1 / 3)

    elif event_type == 'End of Normal Service':
        event_time = clock + exponential(1 / 7)

    elif event_type == 'End of Technical Service':
        event_time = clock + exponential(1 / 10)

    else:
        event_time = clock + 8 * 60

    new_event = {'Event Type': event_type, 'Event Time': event_time, 'Customer': customer}
    future_event_list.append(new_event)


def remove_abandon(future_event_list, customer):
    for i in future_event_list:
        if (i['Event Type'] == 'Abandon') & (i['Customer'] == customer):
            future_event_list.remove(i)


def arrival(future_event_list, state, clock, data, customer, params):

    data['Customers'][customer] = dict()
    data['Customers'][customer]['Arrival Time'] = clock  # track every move of this customer
    data['Customers'][customer]['Type'] = is_VIP()
    data['Customers'][customer]['Has Waited'] = False
    data['Customers'][customer]['Used Call-back'] = False

    if data['Customers'][customer]['Type'] == 'Normal':

        data['Cumulative Stats']['Total Number of Normal Customers'] += 1

        if state['Normal Operators Serving'] < params["Number of Normal Operators"]:
            state['Normal Operators Serving'] += 1
            fel_maker(future_event_list, 'End of Normal Service', state, clock, customer)
            data['Customers'][customer]['Time Service Begins'] = clock
            data['Cumulative Stats']['Service Starters']['Normal Q'] += 1

        elif state['Expert Operators Serving'] < params["Number of Expert Operators"]:
            state['Expert Operators Serving'] += 1
            fel_maker(future_event_list, 'End of Expert Service', state, clock, customer)
            data['Customers'][customer]['Time Service Begins'] = clock
            data['Cumulative Stats']['Service Starters']['Normal Q'] += 1
            data['Cumulative Stats']['Number of Normal Customers Served by Expert Operators'] += 1

        else:

            if (state['Normal QL'] > 4) & (use_callback()):
                data['Customers'][customer]['Used Call-back'] = True
                data['Cumulative Stats']['Area Under QL Curve']['Normal Call-back Q'] += \
                    state['Normal Call-back QL'] * (clock - data['Last Time QL Changed']['Normal Call-back Q'])
                state['Normal Call-back QL'] += 1
                data['Queue Customers']['Normal Call-back Q'][customer] = clock  # add this customer to the queue
                data['Last Time QL Changed']['Normal Call-back Q'] = clock
                if state['Normal Call-back QL'] > data['Maximum QL']['Normal Call-back Q']:
                    data['Maximum QL']['Normal Call-back Q'] = state['Normal Call-back QL']

            else:
                data['Cumulative Stats']['Area Under QL Curve']['Normal Q'] += \
                    state['Normal QL'] * (clock - data['Last Time QL Changed']['Normal Q'])
                state['Normal QL'] += 1
                data['Queue Customers']['Normal Q'][customer] = clock  # add this customer to the queue
                data['Last Time QL Changed']['Normal Q'] = clock
                if state['Normal QL'] > data['Maximum QL']['Normal Q']:
                    data['Maximum QL']['Normal Q'] = state['Normal QL']
                if will_abandon():
                    fel_maker(future_event_list, 'Abandon', state, clock, customer, data)

            data['Customers'][customer]['Has Waited'] = True

    else:

        data['Cumulative Stats']['Total Number of VIP Customers'] += 1

        if state['Expert Operators Serving'] < params["Number of Expert Operators"]:

            data['Cumulative Stats']['Number of VIP Customers Not Using Call-back'] += 1
            state['Expert Operators Serving'] += 1
            fel_maker(future_event_list, 'End of Expert Service', state, clock, customer)
            data['Customers'][customer]['Time Service Begins'] = clock
            data['Cumulative Stats']['Service Starters']['VIP Q'] += 1

        else:

            if (state['VIP QL'] > 4) & (use_callback()):
                data['Customers'][customer]['Used Call-back'] = True
                data['Cumulative Stats']['Area Under QL Curve']['VIP Call-back Q'] += \
                    state['VIP Call-back QL'] * (clock - data['Last Time QL Changed']['VIP Call-back Q'])
                data['Queue Customers']['VIP Call-back Q'][customer] = clock  # add this customer to the queue
                state['VIP Call-back QL'] += 1
                data['Last Time QL Changed']['VIP Call-back Q'] = clock
                if state['VIP Call-back QL'] > data['Maximum QL']['VIP Call-back Q']:
                    data['Maximum QL']['VIP Call-back Q'] = state['VIP Call-back QL']

            else:
                data['Cumulative Stats']['Number of VIP Customers Not Using Call-back'] += 1
                data['Cumulative Stats']['Area Under QL Curve']['VIP Q'] += \
                    state['VIP QL'] * (clock - data['Last Time QL Changed']['VIP Q'])
                state['VIP QL'] += 1
                data['Queue Customers']['VIP Q'][customer] = clock  # add this customer to the queue
                data['Last Time QL Changed']['VIP Q'] = clock
                if state['VIP QL'] > data['Maximum QL']['VIP Q']:
                    data['Maximum QL']['VIP Q'] = state['VIP QL']
                if will_abandon():
                    fel_maker(future_event_list, 'Abandon', state, clock, customer, data)

            data['Customers'][customer]['Has Waited'] = True

    # Scheduling the next arrival
    # We know the current customer
    # Who will be the next customer? (Ex.: Current Customer = C1 -> Next Customer = C2)
    next_customer = 'C' + str(int(customer[1:]) + 1)
    fel_maker(future_event_list, 'Arrival', state, clock, next_customer)


def abandon(state, clock, data, customer):

    if data['Customers'][customer]['Type'] == 'Normal':
        data['Cumulative Stats']['Area Under QL Curve']['Normal Q'] += \
            state['Normal QL'] * (clock - data['Last Time QL Changed']['Normal Q'])
        data['Queue Customers']['Normal Q'].pop(customer, None)
        state['Normal QL'] -= 1
        data['Last Time QL Changed']['Normal Q'] = clock

    else:
        data['Cumulative Stats']['Area Under QL Curve']['VIP Q'] += \
            state['VIP QL'] * (clock - data['Last Time QL Changed']['VIP Q'])
        data['Queue Customers']['VIP Q'].pop(customer, None)
        state['VIP QL'] -= 1
        data['Last Time QL Changed']['VIP Q'] = clock
        data['Cumulative Stats']['VIP Customers Total Time in System'] +=\
            clock - data['Customers'][customer]['Arrival Time']

    data['Customers'].pop(customer, None)


def end_of_expert_service(future_event_list, state, clock, data, customer, params):

    data['Cumulative Stats']['Server Busy Time']['Expert Operators'] +=\
        clock - data['Customers'][customer]['Time Service Begins']

    if is_technical_needed():

        data['Customers'][customer]['Time Primary Service Ends'] = clock
        if state['Technical Operators Serving'] < params["Number of Technical Operators"]:

            state['Technical Operators Serving'] += 1
            fel_maker(future_event_list, 'End of Technical Service', state, clock, customer)
            data['Customers'][customer]['Time Technical Service Begins'] = clock
            if data['Customers'][customer]['Type'] == 'VIP':
                data['Cumulative Stats']['Service Starters']['VIP Technical Q'] += 1
            else:
                data['Cumulative Stats']['Service Starters']['Normal Technical Q'] += 1

        else:
            if data['Customers'][customer]['Type'] == 'VIP':
                data['Cumulative Stats']['Area Under QL Curve']['VIP Technical Q'] += \
                    state['VIP Technical QL'] * (clock - data['Last Time QL Changed']['VIP Technical Q'])
                state['VIP Technical QL'] += 1
                data['Queue Customers']['VIP Technical Q'][customer] = clock  # add this customer to the queue
                data['Last Time QL Changed']['VIP Technical Q'] = clock
                if state['VIP Technical QL'] > data['Maximum QL']['VIP Technical Q']:
                    data['Maximum QL']['VIP Technical Q'] = state['VIP Technical QL']
            else:
                data['Cumulative Stats']['Area Under QL Curve']['Normal Technical Q'] += \
                    state['Normal Technical QL'] * (clock - data['Last Time QL Changed']['Normal Technical Q'])
                state['Normal Technical QL'] += 1
                data['Queue Customers']['Normal Technical Q'][customer] = clock  # add this customer to the queue
                data['Last Time QL Changed']['Normal Technical Q'] = clock
                if state['Normal Technical QL'] > data['Maximum QL']['Normal Technical Q']:
                    data['Maximum QL']['Normal Technical Q'] = state['Normal Technical QL']

            data['Customers'][customer]['Has Waited'] = True

    else:
        if data['Customers'][customer]['Type'] == 'VIP':
            if not data['Customers'][customer]['Used Call-back']:
                data['Cumulative Stats']['VIP Customers Total Time in System'] +=\
                    clock - data['Customers'][customer]['Arrival Time']
            if not data['Customers'][customer]['Has Waited']:
                data['Cumulative Stats']['Number of VIP Customers Not Waiting'] += 1
        data['Customers'].pop(customer, None)

    if state['VIP QL'] > 0:
        first_customer_in_queue = min(data['Queue Customers']['VIP Q'], key=data['Queue Customers']['VIP Q'].get)
        data['Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['VIP Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Arrival Time']
        data['Cumulative Stats']['Area Under QL Curve']['VIP Q'] += \
            state['VIP QL'] * (clock - data['Last Time QL Changed']['VIP Q'])
        state['VIP QL'] -= 1
        data['Queue Customers']['VIP Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['VIP Q'] = clock
        remove_abandon(future_event_list, first_customer_in_queue)
        data['Cumulative Stats']['Service Starters']['VIP Q'] += 1
        fel_maker(future_event_list, 'End of Expert Service', state, clock, first_customer_in_queue)

    elif state['Normal QL'] > 0:
        first_customer_in_queue = min(data['Queue Customers']['Normal Q'], key=data['Queue Customers']['Normal Q'].get)
        data['Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['Normal Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Arrival Time']
        data['Cumulative Stats']['Area Under QL Curve']['Normal Q'] += \
            state['Normal QL'] * (clock - data['Last Time QL Changed']['Normal Q'])
        state['Normal QL'] -= 1
        data['Queue Customers']['Normal Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['Normal Q'] = clock
        data['Cumulative Stats']['Number of Normal Customers Served by Expert Operators'] += 1
        remove_abandon(future_event_list, first_customer_in_queue)
        data['Cumulative Stats']['Service Starters']['Normal Q'] += 1
        fel_maker(future_event_list, 'End of Expert Service', state, clock, first_customer_in_queue)

    elif state['VIP Call-back QL'] > 0:
        first_customer_in_queue =\
            min(data['Queue Customers']['VIP Call-back Q'], key=data['Queue Customers']['VIP Call-back Q'].get)
        data['Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['VIP Call-back Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Arrival Time']
        data['Cumulative Stats']['Area Under QL Curve']['VIP Call-back Q'] += \
            state['VIP Call-back QL'] * (clock - data['Last Time QL Changed']['VIP Call-back Q'])
        state['VIP Call-back QL'] -= 1
        data['Queue Customers']['VIP Call-back Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['VIP Call-back Q'] = clock
        data['Cumulative Stats']['Service Starters']['VIP Call-back Q'] += 1
        fel_maker(future_event_list, 'End of Expert Service', state, clock, first_customer_in_queue)

    elif state['Normal Call-back QL'] > 0:
        first_customer_in_queue =\
            min(data['Queue Customers']['Normal Call-back Q'], key=data['Queue Customers']['Normal Call-back Q'].get)
        data['Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['Normal Call-back Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Arrival Time']
        data['Cumulative Stats']['Area Under QL Curve']['Normal Call-back Q'] += \
            state['Normal Call-back QL'] * (clock - data['Last Time QL Changed']['Normal Call-back Q'])
        state['Normal Call-back QL'] -= 1
        data['Queue Customers']['Normal Call-back Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['Normal Call-back Q'] = clock
        data['Cumulative Stats']['Number of Normal Customers Served by Expert Operators'] += 1
        data['Cumulative Stats']['Service Starters']['Normal Call-back Q'] += 1
        fel_maker(future_event_list, 'End of Expert Service', state, clock, first_customer_in_queue)

    else:
        state['Expert Operators Serving'] -= 1


def end_of_normal_service(future_event_list, state, clock, data, customer, params):

    data['Cumulative Stats']['Server Busy Time']['Normal Operators'] +=\
        clock - data['Customers'][customer]['Time Service Begins']

    if is_technical_needed():

        data['Customers'][customer]['Time Primary Service Ends'] = clock
        if state['Technical Operators Serving'] < params["Number of Technical Operators"]:
            state['Technical Operators Serving'] += 1
            fel_maker(future_event_list, 'End of Technical Service', state, clock, customer)
            data['Customers'][customer]['Time Technical Service Begins'] = clock
            data['Cumulative Stats']['Service Starters']['Normal Technical Q'] += 1

        else:
            data['Cumulative Stats']['Area Under QL Curve']['Normal Technical Q'] += \
                state['Normal Technical QL'] * (clock - data['Last Time QL Changed']['Normal Technical Q'])
            state['Normal Technical QL'] += 1
            data['Queue Customers']['Normal Technical Q'][customer] = clock  # add this customer to the queue
            data['Last Time QL Changed']['Normal Technical Q'] = clock
            if state['Normal Technical QL'] > data['Maximum QL']['Normal Technical Q']:
                data['Maximum QL']['Normal Technical Q'] = state['Normal Technical QL']
            data['Customers'][customer]['Has Waited'] = True
    else:
        data['Customers'].pop(customer, None)

    if state['Normal QL'] > 0:
        first_customer_in_queue = min(data['Queue Customers']['Normal Q'], key=data['Queue Customers']['Normal Q'].get)
        data['Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['Normal Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Arrival Time']
        data['Cumulative Stats']['Area Under QL Curve']['Normal Q'] += \
            state['Normal QL'] * (clock - data['Last Time QL Changed']['Normal Q'])
        state['Normal QL'] -= 1
        data['Queue Customers']['Normal Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['Normal Q'] = clock
        data['Cumulative Stats']['Service Starters']['Normal Q'] += 1
        remove_abandon(future_event_list, first_customer_in_queue)
        fel_maker(future_event_list, 'End of Normal Service', state, clock, first_customer_in_queue)

    elif state['Normal Call-back QL'] > 0:
        first_customer_in_queue =\
            min(data['Queue Customers']['Normal Call-back Q'], key=data['Queue Customers']['Normal Call-back Q'].get)
        data['Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['Normal Call-back Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Arrival Time']
        data['Cumulative Stats']['Area Under QL Curve']['Normal Call-back Q'] += \
            state['Normal Call-back QL'] * (clock - data['Last Time QL Changed']['Normal Call-back Q'])
        state['Normal Call-back QL'] -= 1
        data['Queue Customers']['Normal Call-back Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['Normal Call-back Q'] = clock
        data['Cumulative Stats']['Service Starters']['Normal Call-back Q'] += 1
        fel_maker(future_event_list, 'End of Normal Service', state, clock, first_customer_in_queue)

    else:
        state['Normal Operators Serving'] -= 1


def end_of_technical_service(future_event_list, state, clock, data, customer):
    data['Cumulative Stats']['Server Busy Time']['Technical Operators'] += \
        clock - data['Customers'][customer]['Time Technical Service Begins']
    if (data['Customers'][customer]['Type'] == 'VIP') & (not data['Customers'][customer]['Used Call-back']):
        data['Cumulative Stats']['VIP Customers Total Time in System'] +=\
            clock - data['Customers'][customer]['Arrival Time']
        if not data['Customers'][customer]['Has Waited']:
            data['Cumulative Stats']['Number of VIP Customers Not Waiting'] += 1

    if state['VIP Technical QL'] > 0:
        first_customer_in_queue =\
            min(data['Queue Customers']['VIP Technical Q'], key=data['Queue Customers']['VIP Technical Q'].get)
        data['Customers'][first_customer_in_queue]['Time Technical Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['VIP Technical Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Time Primary Service Ends']
        data['Cumulative Stats']['Area Under QL Curve']['VIP Technical Q'] += \
            state['VIP Technical QL'] * (clock - data['Last Time QL Changed']['VIP Technical Q'])
        state['VIP Technical QL'] -= 1
        data['Queue Customers']['VIP Technical Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['VIP Technical Q'] = clock
        data['Cumulative Stats']['Service Starters']['VIP Technical Q'] += 1
        fel_maker(future_event_list, 'End of Technical Service', state, clock, first_customer_in_queue)

    elif state['Normal Technical QL'] > 0:
        first_customer_in_queue =\
            min(data['Queue Customers']['Normal Technical Q'], key=data['Queue Customers']['Normal Technical Q'].get)
        data['Customers'][first_customer_in_queue]['Time Technical Service Begins'] = clock
        data['Cumulative Stats']['Queue Waiting Time']['Normal Technical Q'] += \
            clock - data['Customers'][first_customer_in_queue]['Time Primary Service Ends']
        data['Cumulative Stats']['Area Under QL Curve']['Normal Technical Q'] += \
            state['Normal Technical QL'] * (clock - data['Last Time QL Changed']['Normal Technical Q'])
        state['Normal Technical QL'] -= 1
        data['Queue Customers']['Normal Technical Q'].pop(first_customer_in_queue, None)
        data['Last Time QL Changed']['Normal Technical Q'] = clock
        data['Cumulative Stats']['Service Starters']['Normal Technical Q'] += 1
        fel_maker(future_event_list, 'End of Technical Service', state, clock, first_customer_in_queue)

    else:
        state['Technical Operators Serving'] -= 1


def end_of_shift(future_event_list, state, clock):
    state['Shift'] += 1
    if state['Shift'] < 3:
        fel_maker(future_event_list, 'End of Shift', state, clock)
    else:
        if state['Day'] < 30:
            fel_maker(future_event_list, 'End of Day', state, clock)
        else:
            fel_maker(future_event_list, 'End of Month', state, clock)


def end_of_day(future_event_list, state, clock):
    state['Shift'] = 1
    state['Day'] += 1
    if state['Day'] == state['Disruption Day']:
        state['Disruption'] = 1
    else:
        state['Disruption'] = 0

    fel_maker(future_event_list, 'End of Shift', state, clock)


def end_of_month(future_event_list, state, clock):
    state['Shift'] = 1
    state['Day'] = 1
    state['Disruption Day'] = math.ceil(random.random()*30)
    if state['Day'] == state['Disruption Day']:
        state['Disruption'] = 1
    else:
        state['Disruption'] = 0

    fel_maker(future_event_list, 'End of Shift', state, clock)


def create_row(step, current_event, state, data, future_event_list):
    # This function will create a list, which will eventually become a row of the output Excel file

    sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])

    # What should this row contain?
    # 1. Step, Clock, Event Type and Event Customer
    try:
        row = [step, current_event['Event Time'], current_event['Event Type'], current_event['Customer']]
    except KeyError:
        row = [step, current_event['Event Time'], current_event['Event Type'], '']
    # 2. All state variables
    row.extend(list(state.values()))
    # 3. All Cumulative Stats
    for i in data['Cumulative Stats'].keys():
        try:
            row.extend(list(data['Cumulative Stats'][i].values()))
        except AttributeError:
            row.append(data['Cumulative Stats'][i])

    # row = [step, current_event['Event Type'], current_event['Event Time'],
    #        state['Queue Length'], state['Server Status'], data['Cumulative Stats']['Server Busy Time'],
    #        data['Cumulative Stats']['Queue Waiting Time'],
    #        data['Cumulative Stats']['Area Under Queue Length Curve'], data['Cumulative Stats']['Service Starters']]

    # 4. All events in fel ('Event Time', 'Event Type' & 'Event Customer' for each event)
    for event in sorted_fel:
        row.append(event['Event Time'])
        row.append(event['Event Type'])
        row.append(event['Customer'])
    return row


def justify(table):
    # This function adds blanks to short rows in order to match their lengths to the maximum row length

    # Find maximum row length in the table
    row_max_len = 0
    for row in table:
        if len(row) > row_max_len:
            row_max_len = len(row)

    # For each row, add enough blanks
    for row in table:
        row.extend([""] * (row_max_len - len(row)))


def create_main_header(state, data):
    # This function creates the main part of header (returns a list)
    # A part of header which is used for future events will be created in create_excel()

    # Header consists of ...
    # 1. Step, Clock, Event Type and Event Customer
    header = ['Step', 'Clock', 'Event Type', 'Event Customer']
    # 2. Names of the state variables
    header.extend(list(state.keys()))
    # 3. Names of the cumulative stats
    for i in data['Cumulative Stats'].keys():
        try:
            for j in data['Cumulative Stats'][i].keys():
                header.append(i + ' For ' + j)
        except AttributeError:
            header.append(i)
    # header.extend(list(data['Cumulative Stats'].keys()))
    return header


def create_excel(table, header):
    # This function creates and fine-tunes the Excel output file

    # Find length of each row in the table
    row_len = len(table[0])

    # Find length of header (header does not include cells for fel at this moment)
    header_len = len(header)

    # row_len exceeds header_len by (max_fel_length * 3) (Event Type, Event Time & Customer for each event in FEL)
    # Extend the header with 'Future Event Time', 'Future Event Type', 'Future Event Customer'
    # for each event in the fel with maximum size
    i = 1
    for col in range((row_len - header_len) // 3):
        header.append('Future Event Time ' + str(i))
        header.append('Future Event Type ' + str(i))
        header.append('Future Event Customer ' + str(i))
        i += 1

    # Dealing with the output
    # First create a pandas DataFrame
    df = pd.DataFrame(table, columns=header, index=None)

    # Create a handle to work on the Excel file
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

    # Write out the Excel file to the hard drive
    df.to_excel(writer, sheet_name='Simulation Output', header=False, startrow=1, index=False)

    # Use the handle to get the workbook (just library syntax, can be found with a simple search)
    workbook = writer.book

    # Get the sheet you want to work on
    worksheet = writer.sheets['Simulation Output']

    # Create a cell-formatter object (this will be used for the cells in the header, hence: header_formatter!)
    header_formatter = workbook.add_format()

    # Define whatever format you want
    header_formatter.set_align('center')
    header_formatter.set_align('vcenter')
    header_formatter.set_font('Times New Roman')
    header_formatter.set_bold('True')

    # Write out the column names and apply the format to the cells in the header row
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_formatter)

    # Auto-fit columns
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i - 1, i - 1, width)

    # Create a cell-formatter object for the body of excel file
    main_formatter = workbook.add_format()
    main_formatter.set_align('center')
    main_formatter.set_align('vcenter')
    main_formatter.set_font('Times New Roman')

    # Apply the format to the body cells
    for row in range(1, len(df) + 1):
        worksheet.set_row(row, None, main_formatter)

    # Save your edits
    writer.save()


def get_col_widths(dataframe):
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


def simulation(simulation_time):

    state, future_event_list, data, params = starting_state()
    clock = 0
    table = []  # a list of lists. Each inner list will be a row in the Excel output.
    step = 1  # every event counts as a step.
    future_event_list.append({'Event Type': 'End of Simulation', 'Event Time': simulation_time, 'Customer': None})

    while clock < simulation_time:
        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])
        # print(sorted_fel)
        # print(data)
        current_event = sorted_fel[0]  # find imminent event
        # customer = current_event['Customer'] = None
        clock = current_event['Event Time']  # advance time
        if clock < simulation_time:  # if current_event['Event Type'] != 'End of Simulation'  (Same)
            if current_event['Event Type'] == 'Arrival':
                customer = current_event['Customer']
                arrival(future_event_list, state, clock, data, customer, params)
            elif current_event['Event Type'] == 'Abandon':
                customer = current_event['Customer']
                abandon(state, clock, data, customer)
            elif current_event['Event Type'] == 'End of Normal Service':
                customer = current_event['Customer']
                end_of_normal_service(future_event_list, state, clock, data, customer, params)
            elif current_event['Event Type'] == 'End of Expert Service':
                customer = current_event['Customer']
                end_of_expert_service(future_event_list, state, clock, data, customer, params)
            elif current_event['Event Type'] == 'End of Technical Service':
                customer = current_event['Customer']
                end_of_technical_service(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'End of Shift':
                end_of_shift(future_event_list, state, clock)
            elif current_event['Event Type'] == 'End of Day':
                end_of_day(future_event_list, state, clock)
            elif current_event['Event Type'] == 'End of Month':
                end_of_month(future_event_list, state, clock)
            future_event_list.remove(current_event)
        else:
            future_event_list.clear()

        # create a row in the table
        table.append(create_row(step, current_event, state, data, future_event_list))
        step += 1
        # nice_print(state, current_event)
    print('-------------------------------------------------------------------------------------------------')

    excel_main_header = create_main_header(state, data)
    justify(table)
    create_excel(table, excel_main_header)

    print('Simulation Ended!\n')

    # computing KPIs
    vip_lq = data['Cumulative Stats']['Area Under QL Curve']['VIP Q'] / simulation_time
    normal_lq = data['Cumulative Stats']['Area Under QL Curve']['Normal Q'] / simulation_time
    vip_callback_lq = data['Cumulative Stats']['Area Under QL Curve']['VIP Call-back Q'] / simulation_time
    normal_callback_lq = data['Cumulative Stats']['Area Under QL Curve']['Normal Call-back Q'] / simulation_time
    vip_technical_lq = data['Cumulative Stats']['Area Under QL Curve']['VIP Technical Q'] / simulation_time
    normal_technical_lq = data['Cumulative Stats']['Area Under QL Curve']['Normal Technical Q'] / simulation_time

    vip_wq = data['Cumulative Stats']['Queue Waiting Time']['VIP Q'] / \
             data['Cumulative Stats']['Service Starters']['VIP Q']
    normal_wq = data['Cumulative Stats']['Queue Waiting Time']['Normal Q'] / \
                data['Cumulative Stats']['Service Starters']['Normal Q']
    vip_callback_wq = data['Cumulative Stats']['Queue Waiting Time']['VIP Call-back Q'] / \
                      data['Cumulative Stats']['Service Starters']['VIP Call-back Q']
    normal_callback_wq = data['Cumulative Stats']['Queue Waiting Time']['Normal Call-back Q'] / \
                         data['Cumulative Stats']['Service Starters']['Normal Call-back Q']
    vip_technical_wq = data['Cumulative Stats']['Queue Waiting Time']['VIP Technical Q'] / \
                       data['Cumulative Stats']['Service Starters']['VIP Technical Q']
    normal_technical_wq = data['Cumulative Stats']['Queue Waiting Time']['Normal Technical Q'] / \
                          data['Cumulative Stats']['Service Starters']['Normal Technical Q']

    max_vip_ql = data['Maximum QL']['VIP Q']
    max_normal_ql = data['Maximum QL']['Normal Q']
    max_vip_callback_ql = data['Maximum QL']['VIP Call-back Q']
    max_normal_callback_ql = data['Maximum QL']['Normal Call-back Q']
    max_vip_technical_ql = data['Maximum QL']['VIP Technical Q']
    max_normal_technical_ql = data['Maximum QL']['Normal Technical Q']

    expert_server_utilization = data['Cumulative Stats']['Server Busy Time']['Expert Operators'] / \
        (simulation_time * params['Number of Expert Operators'])
    normal_server_utilization = data['Cumulative Stats']['Server Busy Time']['Normal Operators'] / \
        (simulation_time * params['Number of Normal Operators'])
    technical_server_utilization = data['Cumulative Stats']['Server Busy Time']['Technical Operators'] / \
        (simulation_time * params['Number of Technical Operators'])

    vips_average_time_in_system = data['Cumulative Stats']['VIP Customers Total Time in System'] / \
        data['Cumulative Stats']['Number of VIP Customers Not Using Call-back']

    percentage_of_vips_never_waiting = data['Cumulative Stats']['Number of VIP Customers Not Waiting'] / \
        data['Cumulative Stats']['Total Number of VIP Customers']

    percentage_of_normal_customers_served_by_experts = \
        data['Cumulative Stats']['Number of Normal Customers Served by Expert Operators'] / data['Cumulative Stats']['Total Number of Normal Customers']

    # printing KPIs
    print(f'VIP Lq = {vip_lq}')
    print(f'Normal Lq = {normal_lq}')
    print(f'VIP Call-back Lq = {vip_callback_lq}')
    print(f'Normal Call-back Lq = {normal_callback_lq}')
    print(f'VIP Technical Lq = {vip_technical_lq}')
    print(f'Normal Technical Lq = {normal_technical_lq}')

    print('---------------------------------------------------')

    print(f'VIP Wq = {vip_wq}')
    print(f'Normal Wq = {normal_wq}')
    print(f'VIP Call-back Wq = {vip_callback_wq}')
    print(f'Normal Call-back Wq = {normal_callback_wq}')
    print(f'VIP Technical Wq = {vip_technical_wq}')
    print(f'Normal Technical Wq = {normal_technical_wq}')

    print('---------------------------------------------------')

    print(f'Max VIP Lq = {max_vip_ql}')
    print(f'Max Normal Lq = {max_normal_ql}')
    print(f'Max VIP Call-back Lq = {max_vip_callback_ql}')
    print(f'Max Normal Call-back Lq = {max_normal_callback_ql}')
    print(f'Max VIP Technical Lq = {max_vip_technical_ql}')
    print(f'Max Normal Technical Lq = {max_normal_technical_ql}')

    print('---------------------------------------------------')

    print(f'Expert Operators Utilization = {expert_server_utilization}')
    print(f'Normal Operators Utilization = {normal_server_utilization}')
    print(f'Technical Operators Utilization = {technical_server_utilization}')

    print('---------------------------------------------------')

    print(f'VIPs Average Time In System = {vips_average_time_in_system}')
    print(f'Percentage of VIPs Never Waiting = {percentage_of_vips_never_waiting*100}%')
    print(f'Percentage of Normal Customers Served by Expert Operators = {percentage_of_normal_customers_served_by_experts*100} %')


simulation(30*24*60)

