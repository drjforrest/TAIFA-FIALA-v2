"use client";

import { useState } from "react";
import { Button, Card, CardContent } from "@/components/ui";
import { Mail, User, MessageSquare, Send, CheckCircle } from "lucide-react";

interface FormData {
  name: string;
  email: string;
  organization: string;
  subject: string;
  message: string;
}

export default function ContactForm() {
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    organization: "",
    subject: "",
    message: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<
    "idle" | "success" | "error"
  >("idle");

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      setSubmitStatus("success");

      // Reset form after success
      setTimeout(() => {
        setFormData({
          name: "",
          email: "",
          organization: "",
          subject: "",
          message: "",
        });
        setSubmitStatus("idle");
      }, 3000);
    } catch (error) {
      setSubmitStatus("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputStyles = {
    width: "100%",
    padding: "12px 16px",
    borderRadius: "8px",
    border: "1px solid rgba(255, 255, 255, 0.5)",
    backgroundColor: "rgba(255, 255, 255, 0.9)",
    color: "#1f2937",
    fontSize: "16px",
    backdropFilter: "blur(10px)",
  };

  const labelStyles = {
    display: "block",
    marginBottom: "8px",
    fontSize: "14px",
    fontWeight: "600",
    color: "#1f2937",
  };

  if (submitStatus === "success") {
    return (
      <Card className="max-w-2xl mx-auto bg-white/20 backdrop-blur-sm border border-white/30">
        <CardContent className="p-16 text-center">
          <CheckCircle className="h-16 w-16 mx-auto mb-4 text-green-400" />
          <h3 className="text-2xl font-bold text-white mb-4">
            Message Sent Successfully!
          </h3>
          <p className="text-white/90 mb-6">
            Thank you for reaching out. We'll get back to you within 24-48
            hours.
          </p>
          <Button
            onClick={() => setSubmitStatus("idle")}
            className="bg-white/20 text-white border border-white/30 hover:bg-white/30"
          >
            Send Another Message
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-2xl mx-auto bg-white/20 backdrop-blur-sm border border-white/30 p-16">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Mail className="h-6 w-6 text-gray-800 mr-3" />
            <h3 className="text-2xl font-bold text-gray-800">Get In Touch</h3>
          </div>
          <p className="text-gray-600">
            We'd love to hear from you. Send us a message and we'll respond as
            soon as possible.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label style={labelStyles}>
                <User className="h-4 w-4 inline mr-2" />
                Full Name *
              </label>
              <input
                type="text"
                className="w-full p-3 rounded-lg border border-gray-300 bg-white text-gray-800 placeholder:text-gray-500"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Your full name"
                required
              />
            </div>
            <div>
              <label style={labelStyles}>
                <Mail className="h-4 w-4 inline mr-2" />
                Email Address *
              </label>
              <input
                type="email"
                className="w-full p-3 rounded-lg border border-gray-300 bg-white text-gray-800 placeholder:text-gray-500"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                placeholder="your.email@example.com"
                required
              />
            </div>
          </div>

          <div>
            <label style={labelStyles}>Organization</label>
            <input
              type="text"
              className="w-full p-3 rounded-lg border border-gray-300 bg-white text-gray-800 placeholder:text-gray-500"
              value={formData.organization}
              onChange={(e) =>
                handleInputChange("organization", e.target.value)
              }
              placeholder="Your organization or company (optional)"
            />
          </div>

          <div>
            <label style={labelStyles}>
              <MessageSquare className="h-4 w-4 inline mr-2" />
              Subject *
            </label>
            <select
              className="w-full p-3 rounded-lg border border-gray-300 bg-white text-gray-800"
              value={formData.subject}
              onChange={(e) => handleInputChange("subject", e.target.value)}
              required
            >
              <option
                value=""
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                Select a subject
              </option>
              <option
                value="partnership"
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                Partnership Opportunities
              </option>
              <option
                value="funding"
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                Funding & Support
              </option>
              <option
                value="research"
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                Research Collaboration
              </option>
              <option
                value="data"
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                Data Contribution
              </option>
              <option
                value="media"
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                Media & Press
              </option>
              <option
                value="general"
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                General Inquiry
              </option>
              <option
                value="other"
                style={{ color: "#374151", backgroundColor: "white" }}
              >
                Other
              </option>
            </select>
          </div>

          <div>
            <label style={labelStyles}>Message *</label>
            <textarea
              className="w-full p-3 rounded-lg border border-gray-300 bg-white text-gray-800 placeholder:text-gray-500 min-h-[120px] resize-vertical"
              value={formData.message}
              onChange={(e) => handleInputChange("message", e.target.value)}
              placeholder="Tell us about your interest in TAIFA-FIALA and how we might work together..."
              rows={5}
              required
            />
          </div>

          {submitStatus === "error" && (
            <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
              <p className="text-red-200 text-sm">
                There was an error sending your message. Please try again or
                contact us directly.
              </p>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-white text-gray-900 hover:bg-white/90 font-semibold"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900 mr-2"></div>
                  Sending...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Message
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="border-gray-300 text-gray-800 hover:bg-gray-50 bg-white"
              onClick={() => {
                setFormData({
                  name: "",
                  email: "",
                  organization: "",
                  subject: "",
                  message: "",
                });
                setSubmitStatus("idle");
              }}
            >
              Clear Form
            </Button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              By submitting this form, you agree to our privacy policy and terms
              of service.
            </p>
          </div>
        </form>

        {/* Alternative Contact Methods */}
        <div className="mt-12 pt-8 border-t border-gray-300">
          <div className="text-center mb-6">
            <h4 className="text-lg font-semibold text-gray-800 mb-2">
              Other Ways to Reach Us
            </h4>
            <p className="text-gray-600 text-sm">
              Prefer direct contact? Here are additional ways to get in touch.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
              <Mail className="h-8 w-8 mx-auto mb-2 text-gray-600" />
              <h5 className="font-semibold text-gray-800 mb-1">Email</h5>
              <p className="text-gray-600 text-sm">contact@taifa-fiala.org</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg border border-gray-200">
              <MessageSquare className="h-8 w-8 mx-auto mb-2 text-gray-600" />
              <h5 className="font-semibold text-gray-800 mb-1">Response Time</h5>
              <p className="text-gray-600 text-sm">24-48 hours</p>
            </div>
          </div>
        </div>
    </Card>
  );
}
