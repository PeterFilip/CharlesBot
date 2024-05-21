## TODO:
-Test K8s env
-Redis Cluster
-Configure remote dev for PIs, make them cluster
-LLM API
-Intent Classification API
-REDIS STREAM cluster
-Speech Transcription API
-Scalable Task Queues
-Non-scalable API
-MetalLB load balancer
-SMS API
-Web Server (scalable I guess)

to handle ws reconnections to same app instance when dropped:
	-either keep enough info in session manager to route to same place
	-or use stick sessions/ws session affinity at LB/ingress level

-provide API to talk with redis/stream instance like I did with mongo

-Have GET endpoint on API that returns info on live command sessions so that
	-any arbitrary worker can reconnect to a live session using data from that
	GET if dropped 

## Architecture Updates:
* More Microservices
* API lighter-weight
* Everything is k8s services
* Redis streams as queue for audio/video frames