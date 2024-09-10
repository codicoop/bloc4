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
        slotEventOverlap: false,
        headerToolbar: {
            left: "today",
            center: "title",
            right: "prev,next",
        },
        views: {
            customTimeGridWeek: {
                type: "timeGridWeek",
                duration: { days: 7 },
                firstDay: 1,
                // selectable: roomId !== "all",
                selectable: true,
                select: function (info) {
                    const start = info.startStr;
                    const end = info.endStr;
                    const today = new Date();
                    const startDate = new Date(info.startStr);
                    const endDate = new Date(info.endStr);
                    if (startDate < today) {
                        alert(
                            "La data triada ha de ser posterior al dia d'avui."
                        );
                    } else if (roomId.length == 36) {
                        const dialog = document.getElementById("confirmation-dialog")
                        const day = startDate.toLocaleDateString();
                        const startHours = startDate
                            .getHours()
                            .toString()
                            .padStart(2, "0");
                        const startMinutes = startDate
                            .getMinutes()
                            .toString()
                            .padStart(2, "0");
                        const endHours = endDate
                            .getHours()
                            .toString()
                            .padStart(2, "0");
                        const endMinutes = endDate
                            .getMinutes()
                            .toString()
                            .padStart(2, "0");
                        
                        // Volem mostrar el dialog
                        showConfirmDialog()
                        dialog.addEventListener("close", (e) => {
                            if (dialog.returnValue === "true") {
                                window.location.href = `${createReservationUrl}?start=${encodeURIComponent(
                                    start
                                )}&end=${encodeURIComponent(
                                    end
                                )}&id=${encodeURIComponent(roomId)}`;
                            }
                        })
                    } else {
                        showAlertNoRoom()
                    }
                },
                selectMirror: false,
                // Time Grid:
                allDaySlot: false,
                slotMinTime: "08:00:00",
                slotMaxTime: "18:00:00",
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
            // let color = info.event._def.extendedProps["color"];
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
            if (info.event.extendedProps.is_staff) {
                window.location.href =
                    reservationViewUrl +
                    info.event.extendedProps.reservation_id;
            }
        },
    });
    calendar.render();
};
document.addEventListener("DOMContentLoaded", loadCalendar);

const addEventSource = (element) => {
    roomId = element.getAttribute("data-id");
    calendar.setOption("selectable", true);
    calendar.removeAllEventSources();
    calendar.addEventSource(`/reserves/ajax/calendar/${roomId}`);
};

const showAlertNoRoom = () => {
    const dialog = document.getElementById("alert-no-room")
    dialog.show()
}
const showConfirmDialog = () => {
    const dialog = document.getElementById("confirmation-dialog")
    dialog.show()
}
