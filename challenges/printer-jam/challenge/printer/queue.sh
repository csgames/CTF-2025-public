#!/bin/bash

#
# Copyright(C) 1993-1996 ZEROZ, Inc.
#
# This program is non-free software; you cannot redistribute it and/or
# modify it under the terms of the ZEROZ License
# as published by the ZEROZ Foundation.
#
# DESCRIPTION:
#   Queues a new page to the printer and unqueues old page.
#

if [ -e /printer/page.old ]; then /usr/bin/rm -f /printer/page.old || : ; fi
/usr/bin/mv -f /printer/page /printer/page.old
/usr/bin/mv "${1}" /printer/page
/usr/bin/chown --reference=/printer/page.old /printer/page
/usr/bin/chmod --reference=/printer/page.old /printer/page
