import { useState } from "react";
import { Search, Eye, CheckCircle, XCircle, Clock } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

type ConsultationStatus = "pending" | "confirmed" | "cancelled";

interface Consultation {
  id: string;
  name: string;
  email: string;
  phone: string;
  preferredDate: string;
  preferredTime: string;
  message: string;
  status: ConsultationStatus;
  createdAt: string;
}

const MOCK_CONSULTATIONS: Consultation[] = [
  { id: "CON-001", name: "Aisha Mohammed", email: "aisha@email.com", phone: "055 123 4567", preferredDate: "2026-03-20", preferredTime: "Morning (10AM – 12PM)", message: "Looking for a bridal gown for my June wedding.", status: "pending", createdAt: "2026-03-10" },
  { id: "CON-002", name: "Sara Al Mansoori", email: "sara@email.com", phone: "050 987 6543", preferredDate: "2026-03-22", preferredTime: "Afternoon (12PM – 4PM)", message: "Interested in renting an evening dress for a gala.", status: "confirmed", createdAt: "2026-03-09" },
  { id: "CON-003", name: "Maryam Khan", email: "maryam@email.com", phone: "056 111 2233", preferredDate: "2026-03-25", preferredTime: "Evening (4PM – 8PM)", message: "", status: "pending", createdAt: "2026-03-08" },
  { id: "CON-004", name: "Huda Ibrahim", email: "huda@email.com", phone: "052 444 5566", preferredDate: "2026-03-18", preferredTime: "Morning (10AM – 12PM)", message: "Want to see the new bridal collection.", status: "cancelled", createdAt: "2026-03-07" },
];

export default function AdminConsultations() {
  const [consultations, setConsultations] = useState<Consultation[]>(MOCK_CONSULTATIONS);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedConsultation, setSelectedConsultation] = useState<Consultation | null>(null);
  const { toast } = useToast();

  const filtered = consultations.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const updateStatus = (id: string, status: ConsultationStatus) => {
    setConsultations(prev => prev.map(c => c.id === id ? { ...c, status } : c));
    setSelectedConsultation(null);
    toast({
      title: status === "confirmed" ? "Consultation Confirmed" : "Consultation Cancelled",
      description: `The appointment has been ${status}.`,
    });
  };

  const statusConfig = {
    pending: { label: "Pending", class: "bg-yellow-100 text-yellow-800", icon: Clock },
    confirmed: { label: "Confirmed", class: "bg-green-100 text-green-800", icon: CheckCircle },
    cancelled: { label: "Cancelled", class: "bg-red-100 text-red-800", icon: XCircle },
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-heading font-semibold text-gray-900">Consultation Requests</h1>
        <p className="text-sm text-gray-500 mt-1">Manage private viewing appointments.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {(["pending", "confirmed", "cancelled"] as const).map(status => {
          const config = statusConfig[status];
          const Icon = config.icon;
          const count = consultations.filter(c => c.status === status).length;
          return (
            <div key={status} className="bg-white border border-border rounded-xl p-4 flex items-center gap-4">
              <div className={`w-10 h-10 rounded-full ${config.class} flex items-center justify-center`}>
                <Icon size={18} />
              </div>
              <div>
                <p className="text-2xl font-heading font-semibold">{count}</p>
                <p className="text-xs text-gray-500 uppercase tracking-wider">{config.label}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
        {/* Search */}
        <div className="p-4 border-b border-border bg-gray-50/50">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-border rounded-md text-sm focus:outline-none focus:border-gold transition-colors"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-500 font-medium border-b border-border uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-6 py-4">Client</th>
                <th className="px-6 py-4">Date & Time</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Submitted</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map(c => {
                const config = statusConfig[c.status];
                return (
                  <tr key={c.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{c.name}</p>
                      <p className="text-gray-500 text-xs">{c.email}</p>
                    </td>
                    <td className="px-6 py-4">
                      <p>{c.preferredDate}</p>
                      <p className="text-gray-500 text-xs">{c.preferredTime}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${config.class}`}>
                        {config.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-500">{c.createdAt}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => setSelectedConsultation(c)} className="text-gray-500 hover:text-gold transition-colors p-1" title="View details">
                          <Eye size={18} />
                        </button>
                        {c.status === "pending" && (
                          <>
                            <button onClick={() => updateStatus(c.id, "confirmed")} className="text-green-600 hover:text-green-700 transition-colors p-1" title="Confirm">
                              <CheckCircle size={18} />
                            </button>
                            <button onClick={() => updateStatus(c.id, "cancelled")} className="text-red-500 hover:text-red-600 transition-colors p-1" title="Cancel">
                              <XCircle size={18} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">No consultations found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedConsultation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4">
            <div className="flex justify-between items-start">
              <h2 className="font-heading text-xl font-semibold">{selectedConsultation.name}</h2>
              <button onClick={() => setSelectedConsultation(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="space-y-3 text-sm">
              <p><span className="font-medium text-gray-700">Email:</span> {selectedConsultation.email}</p>
              <p><span className="font-medium text-gray-700">Phone:</span> {selectedConsultation.phone}</p>
              <p><span className="font-medium text-gray-700">Preferred Date:</span> {selectedConsultation.preferredDate}</p>
              <p><span className="font-medium text-gray-700">Time Slot:</span> {selectedConsultation.preferredTime}</p>
              {selectedConsultation.message && (
                <div>
                  <p className="font-medium text-gray-700 mb-1">Message:</p>
                  <p className="bg-gray-50 p-3 rounded-md text-gray-600 italic">{selectedConsultation.message}</p>
                </div>
              )}
            </div>
            {selectedConsultation.status === "pending" && (
              <div className="flex gap-3 pt-2">
                <button onClick={() => updateStatus(selectedConsultation.id, "confirmed")} className="flex-1 py-2.5 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 transition-colors">
                  Confirm
                </button>
                <button onClick={() => updateStatus(selectedConsultation.id, "cancelled")} className="flex-1 py-2.5 bg-red-500 text-white rounded-md text-sm font-medium hover:bg-red-600 transition-colors">
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
