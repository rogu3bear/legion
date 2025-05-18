import asyncio
import time
from datetime import datetime

from legion.agents.base import BaseAgent


class HealthcheckAgent(BaseAgent):
    """Agent responsible for monitoring system health and uptime."""

    SYSTEM_PROMPT = """You are the Healthcheck Agent, responsible for:
    1. Monitoring system uptime and performance
    2. Alerting on issues or anomalies
    3. Maintaining system health metrics
    4. Providing status reports
    """

    def __init__(self, orchestrator, llm_client=None, **kwargs):
        super().__init__(orchestrator, llm_client)
        self.start_time = time.time()
        self.check_interval = self.config.get(
            "check_interval", 300
        )  # 5 minutes default
        self.health_task = None

    async def start(self):
        """Start the health monitoring loop."""
        if not self.health_task:
            self.health_task = asyncio.create_task(self.health_loop())
            self.logger.info("Health monitoring started")

    async def stop(self):
        """Stop the health monitoring loop."""
        if self.health_task:
            self.health_task.cancel()
            try:
                await self.health_task
            except asyncio.CancelledError:
                pass
            self.health_task = None
            self.logger.info("Health monitoring stopped")

    async def health_loop(self):
        """Main health monitoring loop."""
        while True:
            try:
                uptime = time.time() - self.start_time
                threshold = self.config.get("uptime_threshold", 3600)

                if uptime < threshold:
                    message = f"⚠️ System uptime ({uptime:.2f}s) below threshold ({threshold}s)"
                    await self.post_to_discord(message)
                else:
                    message = f"✅ System healthy - Uptime: {uptime:.2f}s"
                    await self.post_to_discord(message)

                # Log metrics
                self.logger.info(f"Health check - Uptime: {uptime:.2f}s")

                # Sleep for check interval using config with default
                interval = self.config.get("check_interval", 300)
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.logger.error(f"Error in health loop: {e}")
                await asyncio.sleep(60)  # Back off on error

    async def get_status(self):
        """Get current system status."""
        uptime = time.time() - self.start_time
        return {
            "uptime": uptime,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "healthy": uptime >= self.config.get("uptime_threshold", 3600),
            "monitoring_active": self.health_task is not None
            and not self.health_task.done(),
        }

    async def check_dependencies(self):
        """Check status of system dependencies."""
        deps = {"memory": False, "llm": False, "discord": False}

        # Check memory
        if self.memory:
            try:
                await self.memory.ping()
                deps["memory"] = True
            except:
                self.logger.error("Memory check failed")

        # Check LLM
        if self.llm:
            try:
                response = await self.call_llm(
                    thread_id="health_check",
                    history=[{"role": "user", "content": "ping"}],
                    temperature=0.1,
                    max_tokens=10,
                )
                deps["llm"] = bool(response)
            except:
                self.logger.error("LLM check failed")

        # Check Discord
        if self.orchestrator:
            try:
                await self.post_to_discord(
                    "Health check ping", channel="health_check_channel"
                )
                deps["discord"] = True
            except:
                self.logger.error("Discord check failed")

        return deps

    async def generate_report(self):
        """Generate comprehensive health report."""
        status = await self.get_status()
        deps = await self.check_dependencies()

        report = [
            "System Health Report",
            "-------------------",
            f"Uptime: {status['uptime']:.2f}s",
            f"Start Time: {status['start_time']}",
            f"Status: {'HEALTHY' if status['healthy'] else 'WARNING'}",
            f"Monitoring: {'ACTIVE' if status['monitoring_active'] else 'INACTIVE'}",
            "\nDependencies:",
            "-------------",
            f"Memory: {'✅' if deps['memory'] else '❌'}",
            f"LLM: {'✅' if deps['llm'] else '❌'}",
            f"Discord: {'✅' if deps['discord'] else '❌'}",
        ]

        return "\n".join(report)

    async def handle_healthcheck(self):
        return await self.handle_message(
            content="Please perform a health check and report system status.",
            author=self.name,
            timestamp=None,
        )
