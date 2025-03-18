//
// Copyright(C) 1993-1996 ZEROZ, Inc.
//
// This program is non-free software; you cannot redistribute it and/or
// modify it under the terms of the ZEROZ License
// as published by the ZEROZ Foundation.
//
// DESCRIPTION:
//   Worker to handle printing jobs.
//

#ifndef __WORKER_H__
#define __WORKER_H__

#include <stdint.h>

/**
 * Definition for a worker function.
 */
typedef void (*worker_function_t)(void);

/**
 * Definition for a worker function handle.
 */
typedef struct worker_function_handle_t {
    const uint8_t * name;
    const worker_function_t function;
} worker_function_handle_t;

/**
 * Worker function to print a document.
 */
void worker_print(void);

/**
 * Worker function to show debug logs.
 * 
 * NOTE: This function is only active for premium users.
 */
void worker_debug(void);

/**
 * Worker function to enter printer admin mode.
 * 
 * NOTE: This function was mostly disabled due to CVE-1994-6634. Kept for backward compability.
 */
void worker_admin(void);

/**
 * Worker function to exit the worker program.
 */
void worker_exit(void);

/**
 * Worker main loop.
 */
int32_t worker_loop(void);

#endif // __WORKER_H__
