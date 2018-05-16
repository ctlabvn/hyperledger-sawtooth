/**
 * Copyright 2018 Agiletech. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * @file, definition of the Monitor class, which is used to start/stop a monitor to watch the resource consumption
 */

class Cargo {
  constructor(worker, payload, timeout) {
    this.worker = worker;
    this.payload = payload || 10;
    this.timeout = timeout || 1000;

    this.tasks = [];
    this.working = false;
    this.timerRunning = false;
    this.intervalId = null;
  }

  push(data, callback) {
    this.start();
    if (!Array.isArray(data)) {
      data = [data];
    }
    data.forEach(task => {
      this.tasks.push({
        data: task,
        callback: typeof callback === "function" ? callback : null
      });
      // max message count reached
      if (this.tasks.length === this.payload) {
        this.process();
      }
    });
  }

  process() {
    if (this.working) return;
    // stops and if empty it will start again after data are added

    this.stop();
    if (this.tasks.length === 0) return;

    // by default process all
    const ts =
      typeof this.payload === "number"
        ? this.tasks.splice(0, this.payload)
        : this.tasks.splice(0, this.tasks.length);

    const ds = ts.map(task => task.data);
    const callback = function() {
      this.working = false;
      // pass all arguments to callback
      const args = arguments;
      ts.forEach(data => {
        if (data.callback) {
          data.callback.apply(null, args);
        }
      });
      this.start();
      this.process();
    };

    this.working = true;
    this.worker(ds, callback.bind(this));
  }

  start() {
    if (this.timerRunning) return;

    this.timerRunning = true;
    this.intervalId = setInterval(this.process.bind(this), this.timeout);
  }

  stop() {
    if (!this.timerRunning) return;

    this.timerRunning = false;
    clearInterval(this.intervalId);
  }
}

module.exports = Cargo;
