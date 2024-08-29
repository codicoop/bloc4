let calendar;
const loadCalendar = () => {
    const calendarEl = document.getElementById("calendar");
    if (!roomId) {
        roomId = "all";
    }
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "customTimeGridWeek",
        locale: "ca",
        firstDay: 1,
        headerToolbar: {
            left: "prev",
            center: "title",
            right: "next",
        },
        views: {
            customTimeGridWeek: {
                type: "timeGridWeek",
                duration: { days: 7 },
                firstDay: 1,
                selectable: roomId ? true : false,
                select: function (info) {
                    const start = info.startStr;
                    const end = info.endStr;
                    window.location.href = `${createReservationUrl}?start=${encodeURIComponent(
                        start
                    )}&end=${encodeURIComponent(end)}&id=${encodeURIComponent(
                        roomId
                    )}`;
                },
                selectMirror: false,
                // Time Grid:
                allDaySlot: false,
                slotMaxTime: "18:00:00",
                slotMinTime: "08:00:00",
                expandRows: true,
            },
        },
        weekends: true,
        initialDate: (function () {
            let currentDate = new Date();
            let day = currentDate.getDay();
            let diff = currentDate.getDate() - day + (day === 0 ? -6 : 1);
            return new Date(currentDate.setDate(diff));
        })(),
        events: {
            url: `/reserves/ajax/calendar/${roomId}`,
            error: function () {
                alert(
                    "No s'han pogut carregar les reserves. Recarrega la pàgina i si d'aquí uns minuts segueix fallant, si us plau avisa'ns."
                );
            },
        },
        eventDidMount: function (info) {
            let pill = document.createElement("span");
            let room = info.event._def.extendedProps["room"];
            let color = info.event._def.extendedProps["color"];
            let eventText = info.el.querySelector(".fc-event-time");

            pill.classList.add("text-xs");
            pill.innerText = room;
            eventText.append(pill);
            eventText.classList.add(
                "flex",
                "flex-wrap",
                "gap-1",
                "items-center"
            );
        },
        eventClick: function (info) {
            const eventObj = info.event;
            if (eventObj.url) {
                window.open(eventObj.url);
                info.jsEvent.preventDefault(); // prevents browser from following link in current tab.
            }
        },
    });
    calendar.render();
};
document.addEventListener("DOMContentLoaded", loadCalendar);

const addEventSource = (element) => {
    roomId = element.getAttribute("id");
    calendar.setOption("selectable", true);
    if (roomId.length < 36) calendar.setOption("selectable", false);
    calendar.removeAllEventSources();
    calendar.addEventSource(`/reserves/ajax/calendar/${roomId}`);
};
