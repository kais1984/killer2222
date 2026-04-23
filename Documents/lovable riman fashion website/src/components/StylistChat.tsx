import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, User, Calendar, ShoppingBag, Ruler, Palette, ChevronRight, Bell, Minimize2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Message {
  id: string;
  sender: "user" | "stylist";
  text: string;
  timestamp: Date;
  action?: {
    label: string;
    url: string;
  };
}

const initialMessages: Message[] = [
  {
    id: "1",
    sender: "stylist",
    text: "Hello! Welcome to Riman Fashion. I'm Sarah, your personal styling consultant. How can I help you today?",
    timestamp: new Date(),
  },
];

const quickReplies = [
  { label: "Book Consultation", action: "/contact", icon: Calendar },
  { label: "Browse Collection", action: "/collection/bridal", icon: ShoppingBag },
  { label: "Size Guide", action: "/alterations", icon: Ruler },
  { label: "Our Fabrics", action: "/atelier", icon: Palette },
];

const StylistChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [newMessage, setNewMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
      const parsed = JSON.parse(saved);
      const withDates = parsed.map((m: Message) => ({ ...m, timestamp: new Date(m.timestamp) }));
      setMessages(withDates);
    }
  }, []);

  useEffect(() => {
    if (messages.length > 1) {
      localStorage.setItem('chatHistory', JSON.stringify(messages.slice(-50)));
    }
  }, [messages]);

  useEffect(() => {
    if (isOpen && hasUnread) {
      setHasUnread(false);
    }
  }, [isOpen, hasUnread]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const simulateTyping = (message: string = "", actionUrl?: string) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const responses: Record<string, { text: string; action?: string }> = {
        "Book Consultation": { text: "Wonderful! I'd love to help you find your dream dress. Let me take you to our booking page.", action: "/contact" },
        "Browse Collection": { text: "Our collection features exclusive bridal gowns, evening dresses, and rental options. Let me show you our bridal collection.", action: "/collection/bridal" },
        "Size Guide": { text: "We offer made-to-measure alterations with every dress purchase! Here's our comprehensive size guide.", action: "/alterations" },
        "Our Fabrics": { text: "We source the finest fabrics from Europe including pure silk, French lace, mikado satin, and delicate chiffon.", action: "/atelier" },
        "I'd like to book a consultation": { text: "Wonderful! We'd love to help you find your dream dress. You can book a private consultation at our Sharjah atelier.", action: "/contact" },
        "Tell me about your collection": { text: "Our collection features exclusive bridal gowns, evening dresses, and rental options. Each piece is crafted with European fabrics.", action: "/collection/bridal" },
        "I have a question about sizing": { text: "We offer made-to-measure alterations with every dress purchase! Our size guide can help you select your starting size.", action: "/alterations" },
        "What fabrics do you offer?": { text: "We source the finest fabrics from Europe including pure silk, French lace, mikado satin, and delicate chiffon. Each dress can be customized.", action: "/atelier" },
      };
      
      const response = responses[message] || { text: "Thank you for your message! Our team will get back to you shortly. In the meantime, feel free to browse our collection or book a consultation." };
      
      const stylistMessage: Message = {
        id: Date.now().toString(),
        sender: "stylist",
        text: response.text,
        timestamp: new Date(),
        action: response.action ? { label: "View", url: response.action } : undefined,
      };
      setMessages((prev) => [...prev, stylistMessage]);
    }, 1500);
  };

  const handleSend = () => {
    if (!newMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: newMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    const msg = newMessage;
    setNewMessage("");
    simulateTyping(msg);
  };

  const handleQuickReply = (reply: { label: string; action: string; icon: React.ElementType }) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: reply.label,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    simulateTyping(reply.label, reply.action);
  };

  const handleActionClick = (url: string) => {
    setIsOpen(false);
    navigate(url);
  };

  return (
    <>
      {/* Chat Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gold text-white rounded-full shadow-lg flex items-center justify-center hover:bg-gold/90 transition-colors"
        aria-label="Chat with stylist"
      >
        {hasUnread && (
          <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 rounded-full border-2 border-white" />
        )}
        <MessageCircle size={28} />
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] bg-white rounded-2xl shadow-2xl border border-border overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gold text-white p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <User size={20} />
                </div>
                <div>
                  <h3 className="font-heading text-sm">Sarah</h3>
                  <p className="text-[10px] text-white/80">Personal Stylist</p>
                </div>
              </div>
              <div className="flex gap-1">
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-2 hover:bg-white/20 rounded-full transition-colors"
                >
                  <Minimize2 size={16} />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-white/20 rounded-full transition-colors"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {!isMinimized && (
              <>
                {/* Messages */}
                <div className="h-80 overflow-y-auto p-4 space-y-4 bg-gray-50">
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] p-3 rounded-2xl ${
                          message.sender === "user"
                            ? "bg-gold text-white rounded-br-sm"
                            : "bg-white border border-border rounded-bl-sm"
                        }`}
                      >
                        <p className="text-sm font-body">{message.text}</p>
                        {message.action && (
                          <button
                            onClick={() => handleActionClick(message.action!.url)}
                            className="mt-2 text-xs underline flex items-center gap-1"
                          >
                            {message.action.label} <ChevronRight size={12} />
                          </button>
                        )}
                        <p className={`text-[10px] mt-1 ${message.sender === "user" ? "text-white/70" : "text-muted-foreground"}`}>
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-white border border-border p-3 rounded-2xl rounded-bl-sm">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-gold/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                          <span className="w-2 h-2 bg-gold/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                          <span className="w-2 h-2 bg-gold/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Quick Replies */}
                <div className="p-3 border-t border-border bg-white">
                  <div className="flex flex-wrap gap-2 mb-3">
                    {quickReplies.map((reply) => {
                      const Icon = reply.icon;
                      return (
                        <button
                          key={reply.label}
                          onClick={() => handleQuickReply(reply)}
                          className="px-3 py-1.5 bg-gray-100 hover:bg-gold/10 hover:text-gold text-xs rounded-full transition-colors flex items-center gap-1"
                        >
                          <Icon size={12} />
                          {reply.label}
                        </button>
                      );
                    })}
                  </div>
                  
                  {/* Input */}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && handleSend()}
                      placeholder="Type your message..."
                      className="flex-1 px-4 py-2 border border-border rounded-full text-sm focus:outline-none focus:border-gold"
                    />
                    <button
                      onClick={handleSend}
                      disabled={!newMessage.trim()}
                      className="w-10 h-10 bg-gold text-white rounded-full flex items-center justify-center hover:bg-gold/90 disabled:opacity-50 transition-colors"
                    >
                      <Send size={18} />
                    </button>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default StylistChat;