#!/bin/bash -xe

echo ECS_CLUSTER=<<{"Ref": "EcsCluster"}>> >> /etc/ecs/ecs.config

yum install -y amazon-efs-utils

mkdir /opt/minecraft

mount -t efs <<{"Ref": "Efs"}>>:/ /opt/minecraft

chown 1000:1000 /opt/minecraft