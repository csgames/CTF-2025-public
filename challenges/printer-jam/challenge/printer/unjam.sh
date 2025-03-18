#!/bin/bash

#
# Copyright(C) 1993-1996 ZEROZ, Inc.
#
# This program is non-free software; you cannot redistribute it and/or
# modify it under the terms of the ZEROZ License
# as published by the ZEROZ Foundation.
#
# DESCRIPTION:
#   Unjams stuck page in printer.
#

/usr/bin/rm -rf /printer/page /printer/page.old
/usr/bin/touch /printer/page
/usr/bin/chown root:root /printer/page
/usr/bin/chmod 777 /printer/page
