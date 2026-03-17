/**
 * Optional background delegation plugin placeholder for the Cells bundle.
 *
 * Replace this file with a full OpenCode plugin implementation when your host
 * environment supports `delegate`, `delegation_read`, and `delegation_list`.
 * The bundle keeps synchronous `task` fallback canonical when this plugin is
 * absent or inert.
 */

export default function backgroundAgentsPlugin() {
  return {
    name: "cells-background-agents-placeholder",
    description:
      "Placeholder plugin that keeps Cells task fallback safe when background delegation is unavailable.",
  };
}
