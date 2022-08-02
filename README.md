# Consuming Terraform Cloud Audit Train API

This is a proof of concept log shipper to demonstrate the principles required to consume the TFC Audit Trail API. It is a work in progress and not suitable for production!

Some reasons off-the-shelf log shippers might not work with this API:
- The API is stateless, so is unable to send only new logs to a specific client
- TFC retains events for 14 days 
- If polled every minute, each event would be sent >20,000 times over a two week period
- At a minimum, deduplication is required to avoid 20k copies of each event (use `id` field as a fingerprint)
- It’s more efficient to only request new events using the `since` parameter, but this means the shipper needs to be stateful
- The API uses pagination, which is not supported by http_poller input
- The event list is under `data`, not at the root of the JSON document

Logstash ninjas might be able to work around these natively, but I couldn't, hence this script.

The script demonstrates one way to consume the paginated API, stream to stdout and POST to logstash.

## Usage

To run the script, set `TFC_ORG_TOKEN` environment variable to be an org token for your TFC organization, then run the script: `python3 tfc_get_logs.py`. The script will pull all existing events from the API, then pull only new events every 60 seconds. Currently events will be output on stdout, and also HTTP POSTed to a logstash HTTP listener on localhost port 50000.

The corresponding logstash pipeline config looks like this:

```
input {
  http {
    host => "0.0.0.0"
    port => 50000
    codec => json {
        target => "[tfcevent]"
    }
    additional_codecs => {}
  }
}

output {
    elasticsearch {
        hosts => "elasticsearch:9200"
        user => "logstash_internal"
        password => "${LOGSTASH_INTERNAL_PASSWORD}"
    }
}
```

## Issues/to-do

- There is a chance of duplicate messages being forwarded in the event that events are added between pages. This could be deduplicated by elastic by setting the document id to be the uuid of the event.
- Events with metadata including a `workspace` key are not processed correctly, as elastic is expecting an object instead of a string.
- This might be better implemented as a one-time cloud function called every X seconds instead of a loop, but some persistent would be required to pass the latest timestamp to each new iteration of the function.
