# Configuration of services

## MQTT

Programs that use the AsyncMqttSource, AsyncMqttSink, MqttSink or MqttSource are configured via the configuration file located at `$HOME/.config/heisskleber/mqtt.yaml`
The configuration parameters are host, port, ssl, user and password to establish a connection with the host.

- **qos**: controls whether delivery of messages is acknowledged or not (see docs for details)[https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html].
  - 1: "At most once", where messages are delivered according to the best efforts of the operating environment.
    Message loss can occur.
  - 2: "At least once", where messages are assured to arrive but duplicates can occur.
  - 3: "Exactly once", where messages are assured to arrive exactly once.
- **max_saved_messages**: maximum number of messages that will be saved in the buffer until connection is available.
- **packstyle**: key of the serialization technique to use. Currently only JSON is supported.
- **source_id**: id of the device that will be used to identify the MQTT messages to be used by clients to format the topic.
  Suggested topic format is in the form of `f"/{measurement_type}/{source_id}"`, eg. "/temperature/box-01".
- **topics**: the topics that the mqtt forwarder will subscribe to.

```yaml
# Heisskleber config file for MqttConf
host: mqtt.example.com
port: 8883
ssl: true
user: "user1"
password: "password1"
qos: 0 # quality of service, 0=at most once, 1=at least once, 2=exactly once
timeout_s: 60
retain: false # save last message
max_saved_messages: 100 # buffer messages in until connection available
packstyle: json

# configs only valid for mqtt forwarder
mapping: /deprecated/
source_id: box-01
topics: ["topic1", "topic2"]
```
