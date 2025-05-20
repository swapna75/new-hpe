from src.models.feedback import FeedBack
from . import BaseListener, log
from src.message_queue import BaseMessageQueue
from aiohttp import web


"""
this is the structure of the alert that will be sent by alertmanager
{
  "version": "4",
  "groupKey": <string>,              // key identifying the group of alerts (e.g. to deduplicate)
  "truncatedAlerts": <int>,          // how many alerts have been truncated due to "max_alerts"
  "status": "<resolved|firing>",
  "receiver": <string>,
  "groupLabels": <object>,
  "commonLabels": <object>,
  "commonAnnotations": <object>,
  "externalURL": <string>,           // backlink to the Alertmanager.
  "alerts": [
    {
      "status": "<resolved|firing>",
      "labels": <object>,
      "annotations": <object>,
      "startsAt": "<rfc3339>",
      "endsAt": "<rfc3339>",
      "generatorURL": <string>,      // identifies the entity that caused the alert
      "fingerprint": <string>        // fingerprint to identify the alert
    },
    ...
  ]
}
"""


class HTTPListener(BaseListener):
    def __init__(self, work_queue: BaseMessageQueue) -> None:
        self.work_queue = work_queue
        self.app = web.Application()
        self.fb_handler = None
        self.app.add_routes([web.post("/alerts", self.receive_alert)])
        self.app.add_routes([web.post("/feedback", self.receive_feedback)])

        self.runner = web.AppRunner(self.app)
        self.site = None

    async def listen(self):
        await self.runner.setup()
        host = "0.0.0.0"
        port = 8080
        self.site = web.TCPSite(self.runner, host=host, port=port)
        log.info(f"HTTPListener is running on http://{host}:{port}")
        await self.site.start()

    async def receive_alert(self, request: web.Request):
        try:
            alerts = await request.json()
        except Exception:
            return web.Response(status=400)

        # self.work_queue.put_nowait([Alert(x) for x in alerts])
        self.work_queue.put_nowait(convert_to_alerts(alerts))

        return web.Response(status=200)

    async def receive_feedback(self, request: web.Request):
        """Processes the feedback from json to custom Feedback type and sends to detector"""
        # add logic to change feedback to normal thing
        fb = FeedBack()  # change

        if self.fb_handler:
            self.fb_handler(fb)

    def set_feedback_listner(self, handler):
        self.fb_handler = handler


def convert_to_alerts(json_data):
    return json_data["alerts"]
