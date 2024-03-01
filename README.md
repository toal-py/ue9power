# dashbo
<p>Most relevant directory:</p>
<h2><a href='https://github.com/toal-py/dashbo/tree/main/mypy/power'>mypy/power</a></h2>
<p>Everything in here is based on a Tasmota Power Reader. This device pushes power consumption data via MQTT to my Raspberry Pi where ioBroker handles and saves the incoming data. This data is the basis for all following calculations of my power consumption.</p>
<ul>
    <li><p><a href='https://github.com/toal-py/dashbo/blob/main/mypy/power/cClasses.py'>cClasses</a></p><p>Custom Classes for my project. Contains a logging class (to be overhauled to be less specific to dailyPowerConsumption) and a mailing class. Mainly used for sending mails to notify myself.</p></li>
    <li><p><a href='https://github.com/toal-py/dashbo/blob/main/mypy/power/dailyPowerConsumption.py'>Daily Power Consumption v1</a></p><p>Deprecated script to extract and save the daily power consumption.</p></li>
    <li><p><a href='https://github.com/toal-py/dashbo/blob/main/mypy/power/dailyPowerConsumption_v1.1.py'>Daily Power Consumption v1.1</a></p><p>Run every morning at 6 am by cron. Uses electricity meter readings to calculate daily power consumption and save it in a PostgreSQL database. Updated version v1.1 uses more specific query - even though functionally irrelevant, it was a nice test to see the effect on performance (more than 20% faster!)</p></li>
    <li><p><a href='https://github.com/toal-py/dashbo/blob/main/mypy/power/housekeeping.py'>Housekeeping</a></p><p>Currently not run on regular basis. The idea was to have a script that deletes old values from the database in order for this to not "overflow" and use too much space. Current version deletes all entries in ts_string older than two weeks and completely clears logValues.txt. Might update this to not delete so much and run it manually from time to time.</p></li>
    <li><p><a href='https://github.com/toal-py/dashbo/blob/main/mypy/power/monthlyPowerConsumption.py'>Monthly Power Consumption</a></p><p>Run on the first day of any month at 6:15 am. Calculates monthly power consumption based on daily values and saves them in seperate table. Checks for completeness of month using calendar module.</p></li>
    <li><p><a href='https://github.com/toal-py/dashbo/blob/main/mypy/power/weeklyPowerConsumption.py'>Weekly Power Consumption</a></p><p>Run as executable Docker Container every Monday at 6:15 am. Calculates weekly power consumption based on daily values and saves them in seperate table. Special challenge: How can I tell the system what a 'week' is? Done with calendar module and mapping daily values to list generated through usage of calendar module. Can theoretically be run at any time, inserted values are checked for uniqueness and completeness. Script always checks current month and writes all full weeks to database table.</p></li>
</ul>

<h2>Power Consumption API</h2>
    <p>My very own API for power consumption: <a href='https://web.toal.wtf/power/api'>https://web.toal.wtf/power/api</a></p>
    <h3>Description</h3>
        <p>
        <table>
        <tbody>
        <tr>
        <td>mode</td>
        <td>Available modes: 'd' for day, 'w' for week, 'm' for month.<br> <b>'d'</b> returns value and comment for a single day if that day is available in daily_power table.<br><b>'w'</b> returns either full week from weekly_power table if the specified date is part of a full week or a partial week if the specified date is part of the current week. A full week returns the weekly power consumption and all daily values. A partial week returns the current week's preliminary total as well as the daily values.<br><b>'m'</b> returns either full month from monthly_power table if the specified date is part of a full month or a partial month if the specified date is part of the current month. A full month returns the monthly power consumption without daily values if 'expand' is not specified as True. A partial month returns the current months's preliminary total as well as the daily values.</td>
        </tr>
        <tr>
        <td>date</td>
        <td>Date to be inspected. Must be dd.mm.yyyy format for modes 'd' and 'w'. For mode 'm' it can either be dd.mm.yyyy or just the month number (for all single-digit months with or without leading zero.). In mode 'd', power consumption for that day is returned. In mode 'w', the week that day is part of is returned (both the whole week's consumption and all the days' values of that week). In mode 'm', for dd.mm.yyyy, the month that day is part of is returned. Alternatively, the number of the month can be put in directly. Only the month's power consumption value is returned if it is a full month - the daily values are only included by default if it is a partial month.</td>
        </tr>
        <tr>
        <td>expand</td>
        <td>Only relevant for mode 'm'. If expand == True or 1, all daily values of that full month will be returned as well.</td>
        </tr>
        </tbody>
        </table>
        </p>


<h2>Templates & Views</h2>
    <h3>Caching</h3>
        <p>
        Power Overview is being cached for 6 hours.
        </p>
        <p>
        Each result of an API call is cached for 6 hours.
        </p>
<h2></h2>

Tasmota: TelePeriod 300 -> change interval to 300 seconds

<b>TO BE COMPLETED...</b>
