# victoropspy
VictorOps CLI Program in Python


I wrote this small Python program to help me manage my on-call duties with VictorOps. 

There is still a lot of work that can be done with this program. But as of now, it does everything I need it to do. It's still better than the VictorOps web UI.

##Requirements 
This program requires Python version 3 and the Requests library.
You also need a VictorOps account with an API key and API ID.
http://victorops.force.com/knowledgebase/articles/Getting_Started/API-Getting-Started/
Those settings are saved in a config.yml file that created at first run.


###Examples:
List all active incidents:
````
./victoropspy.py --action list
````
See more debug information:
````
./victoropspy.py --action list --verbosity debug 

````

Filter out results to only incidents with 'currentPhase='ACKED''

````
./victoropspy.py --action list --regex currentPhase='ACKED'
````

Acknowledge all alerts assigned to the user specified in config.yml 

````
./victoropspy.py --action ack-user 
````

Run a command for every matching incident. The strings "HOSTNAME" and "INCIDENTNUMBER" will be replaced by real the information in the incident. You could also wrap this command with 'watch' to periodically poll VictorOps. But don't forget about their API rate limiting.
````
./victoropspy.py --action exec --regex currentPhase='ACKED' --exec 'fixscript HOSTNAME INCIDENTNUMBER'
````

Return all incidents between 2016-06-05T04:20:00Z and 2016-06-05T04:30:00Z
````
./victoropspy.py --action report --report-kv startedAfter=2016-06-05T04:20:00Z startedBefore=2016-06-05T04:30:00Z
````
Here's the current list of keys:
* entityId
* incidentNumber
* startedAfter
* startedBefore
* host
* service
* currentPhase
* routingKey
