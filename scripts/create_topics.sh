#!/bin/bash
/opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic agent.outbound --partitions 1 --replication-factor 1
/opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists --topic agent.inbound --partitions 1 --replication-factor 1
echo "Topics created."
