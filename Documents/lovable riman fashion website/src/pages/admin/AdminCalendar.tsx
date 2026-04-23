import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const MOCK_BOOKINGS = [
  { id: "BK-001", item: "Rosalina Gown", customer: "Layla Ahmed", start: new Date(2026, 2, 15), end: new Date(2026, 2, 18), color: "bg-gold" },
  { id: "BK-002", item: "Lumina Dress", customer: "Nour Hassan", start: new Date(2026, 2, 20), end: new Date(2026, 2, 22), color: "bg-blue-400" },
  { id: "BK-003", item: "Celeste Gown", customer: "Fatima Al-Sayed", start: new Date(2026, 3, 2), end: new Date(2026, 3, 5), color: "bg-emerald-400" },
];

function getDaysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year: number, month: number) {
  return new Date(year, month, 1).getDay();
}

export default function AdminCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date(2026, 2, 1)); // March 2026
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  const getBookingsForDay = (day: number) => {
    const date = new Date(year, month, day);
    return MOCK_BOOKINGS.filter(b => date >= b.start && date <= b.end);
  };

  const monthName = currentDate.toLocaleString("default", { month: "long", year: "numeric" });

  // Build calendar grid
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-heading font-semibold text-gray-900">Rental Calendar</h1>
        <p className="text-sm text-gray-500 mt-1">View all dress bookings at a glance.</p>
      </div>

      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
        {/* Calendar Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-gray-50/50">
          <button onClick={prevMonth} className="p-2 hover:bg-gray-100 rounded-md transition-colors">
            <ChevronLeft size={20} />
          </button>
          <h2 className="font-heading text-xl font-semibold">{monthName}</h2>
          <button onClick={nextMonth} className="p-2 hover:bg-gray-100 rounded-md transition-colors">
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Day Headers */}
        <div className="grid grid-cols-7 border-b border-border">
          {DAYS.map(day => (
            <div key={day} className="py-3 text-center text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7">
          {cells.map((day, i) => {
            const bookings = day ? getBookingsForDay(day) : [];
            const isToday = day && new Date().getDate() === day && new Date().getMonth() === month && new Date().getFullYear() === year;

            return (
              <div
                key={i}
                className={`min-h-[100px] border-b border-r border-border p-2 ${
                  day ? "bg-white hover:bg-gray-50/50" : "bg-gray-50/30"
                } transition-colors`}
              >
                {day && (
                  <>
                    <span className={`inline-flex items-center justify-center w-7 h-7 text-sm ${
                      isToday ? "bg-gold text-white rounded-full font-bold" : "text-gray-700"
                    }`}>
                      {day}
                    </span>
                    <div className="mt-1 space-y-1">
                      {bookings.map(b => (
                        <div
                          key={b.id}
                          className={`${b.color} text-white text-[10px] px-1.5 py-0.5 rounded truncate cursor-pointer hover:opacity-90 transition-opacity`}
                          title={`${b.item} — ${b.customer}`}
                        >
                          {b.item}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-xl border border-border shadow-sm p-4">
        <h3 className="font-heading text-sm font-semibold mb-3 text-gray-700">Active Bookings</h3>
        <div className="space-y-2">
          {MOCK_BOOKINGS.map(b => (
            <div key={b.id} className="flex items-center gap-3 text-sm">
              <span className={`w-3 h-3 rounded-full ${b.color}`} />
              <span className="font-medium text-gray-900">{b.item}</span>
              <span className="text-gray-500">— {b.customer}</span>
              <span className="text-gray-400 ml-auto text-xs">
                {b.start.toLocaleDateString()} – {b.end.toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
