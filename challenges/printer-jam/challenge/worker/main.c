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

#include "main.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * Worker Globals
 */

static bool WORKER_RUNNING = true;
static bool WORKER_PREMIUM = false;

static const worker_function_handle_t WORKER_FUNCTION_HANDLES[] = {
    {
        "Print",
        worker_print
    },
    {
        "Debug",
        worker_debug
    },
    {
        "Admin",
        worker_admin
    },
    {
        "Exit",
        worker_exit
    }
};
static const uint8_t WORKER_FUNCTION_HANDLE_COUNT = sizeof(WORKER_FUNCTION_HANDLES) / sizeof(worker_function_handle_t);

/**
 * Worker Input
 */

static void worker_banner(void) {
    printf(
        "\n"
        "███████ ███████ ██████   ██████  ███████ \n"
        "   ███  ██      ██   ██ ██    ██    ███  \n"
        "  ███   █████   ██████  ██    ██   ███   \n"
        " ███    ██      ██   ██ ██    ██  ███    \n"
        "███████ ███████ ██   ██  ██████  ███████ \n"
        "-----------------------------------------\n"
        "        Copyright(C) 1993-1996           \n"
        "\n"
        "Subscription: %s"
        "\n",
        WORKER_PREMIUM ? "Premium" : "Standard"
    );
}

static void worker_options(void) {
    uint8_t i;

    printf("\nMenu\n\n");

    for (i = 0; i < WORKER_FUNCTION_HANDLE_COUNT; i++) {
        printf("%u) %s\n", i, WORKER_FUNCTION_HANDLES[i].name);
    }

    printf("\n");
}

static uint32_t worker_option(void) {
    uint32_t user_option;
    int32_t args_count;

    do {
        printf("Choose an option:\n");
        args_count = scanf("%u", &user_option);

        // Flushes input till new line if invalid input.
        if (args_count < 1) scanf("%*[^\n]");
    } while (user_option >= WORKER_FUNCTION_HANDLE_COUNT);

    printf("\n");

    return user_option;
}

/**
 * Worker Premium
 */

void worker_check_premium(void) {
    FILE *file = fopen("/home/worker/license", "r");
    if (file == NULL) return;
    fclose(file);

    WORKER_PREMIUM = true;
}

/**
 * Worker Functions
 */

void worker_print(void) {
    uint8_t print_buffer[8192];
    FILE *print_file;
    uint8_t *print_debug = "FLAG1";

    printf("Content:\n");
    scanf("%8191s", print_buffer);

    printf("\nInput:\n");
    printf(print_buffer);
    printf("\n");

    if ((print_file = fopen("/tmp/page", "w")) == NULL) {
        printf("This file should allow writing. Contact ZEROZ.\n");
        return;
    }

    fwrite(print_buffer, strlen(print_buffer), 1, print_file);

    fclose(print_file);

    printf("\nOutput:\n");
    system("sudo /printer/queue.sh /tmp/page && sudo /printer/print.sh");
    printf("\n");
}

void worker_debug(void) {
    uint8_t log_buffer[256];
    FILE *log_file;
    size_t log_file_size;

    if (!WORKER_PREMIUM) {
        printf("This feature requires a premium membership.\n");
        return;
    }

    if ((log_file = fopen("log", "r")) == NULL) {
        printf("This file should exist. Contact ZEROZ.\n");
        return;
    }

    fseek(log_file, 0, SEEK_END);
    log_file_size = ftell(log_file);
    fseek(log_file, 0, SEEK_SET);

    log_file_size = log_file_size < sizeof(log_buffer) ? log_file_size : sizeof(log_buffer);

    fread(log_buffer, log_file_size, 1, log_file);

    fclose(log_file);

    log_buffer[log_file_size - 1] = '\0';

    printf("Log:\n");
    printf(log_buffer);
    printf("\n");
}

static void worker_exec(void) {
    execve("/bin/sh", NULL, NULL);
}

void worker_admin(void) {
    // We had to disable this due to CVE-1994-6634.
    // Unauthorized actors were executing code remotely on our printers...
    // Kept for backward compability.
    printf("This feature is disabled.\n");

    // worker_exec();
}

void worker_exit(void) {
    WORKER_RUNNING = false;
}

/**
 * Worker Main
 */

int32_t worker_loop(void) {
    worker_check_premium();
    worker_banner();

    while (WORKER_RUNNING) {
        worker_options();

        WORKER_FUNCTION_HANDLES[worker_option()].function();
    }

    return 0;
}

int32_t main(int32_t _argc, const uint8_t **_argv) {
    return worker_loop();
}
