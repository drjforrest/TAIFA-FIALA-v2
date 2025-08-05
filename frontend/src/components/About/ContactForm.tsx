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
    color: "var(--color-card-foreground)",
  };

  if (submitStatus === "success") {
    return (
      <Card 
        className="max-w-2xl mx-auto backdrop-blur-sm border"
        style={{
          backgroundColor: "var(--color-success-background)",
          borderColor: "var(--color-success)",
        }}
      >
        <CardContent className="p-16 text-center">
          <CheckCircle 
            className="h-16 w-16 mx-auto mb-4" 
            style={{ color: "var(--color-success)" }}
          />
          <h3 
            className="text-2xl font-bold mb-4"
            style={{ color: "var(--color-success)" }}
          >
            Message Sent Successfully!
          </h3>
          <p 
            className="mb-6 text-lg"
            style={{ color: "var(--color-card-foreground)" }}
          >
            Thank you for reaching out. We'll get back to you within 24-48
            hours.
          </p>
          <Button
            onClick={() => setSubmitStatus("idle")}
            style={{
              backgroundColor: "var(--color-success)",
              color: "var(--color-success-foreground)",
              borderColor: "var(--color-success)",
            }}
            className="hover:opacity-90 transition-opacity duration-200"
          >
            Send Another Message
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      className="max-w-2xl mx-auto backdrop-blur-sm border"
      style={{
        backgroundColor: "var(--color-card)",
        borderColor: "var(--color-primary)",
        padding: "4rem",
      }}
    >
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-6">
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center mr-4"
              style={{
                backgroundColor: "var(--color-primary)",
                color: "var(--color-primary-foreground)",
              }}
            >
              <Mail className="h-6 w-6" />
            </div>
            <h3 
              className="text-3xl font-bold"
              style={{ color: "var(--color-card-foreground)" }}
            >
              Get In Touch
            </h3>
          </div>
          <p 
            className="text-lg leading-relaxed"
            style={{ color: "var(--color-muted-foreground)" }}
          >
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
                className="w-full p-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2"
                style={{
                  backgroundColor: "var(--color-input)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-card-foreground)",
                }}
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Your full name"
                onFocus={(e) => {
                  e.target.style.borderColor = "var(--color-primary)";
                  e.target.style.boxShadow = `0 0 0 2px var(--color-primary-background)`;
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "var(--color-border)";
                  e.target.style.boxShadow = "none";
                }}
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
                className="w-full p-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2"
                style={{
                  backgroundColor: "var(--color-input)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-card-foreground)",
                }}
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                placeholder="your.email@example.com"
                onFocus={(e) => {
                  e.target.style.borderColor = "var(--color-primary)";
                  e.target.style.boxShadow = `0 0 0 2px var(--color-primary-background)`;
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "var(--color-border)";
                  e.target.style.boxShadow = "none";
                }}
                required
              />
            </div>
          </div>

          <div>
            <label style={labelStyles}>Organization</label>
            <input
              type="text"
              className="w-full p-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2"
              style={{
                backgroundColor: "var(--color-input)",
                borderColor: "var(--color-border)",
                color: "var(--color-card-foreground)",
              }}
              value={formData.organization}
              onChange={(e) =>
                handleInputChange("organization", e.target.value)
              }
              placeholder="Your organization or company (optional)"
              onFocus={(e) => {
                e.target.style.borderColor = "var(--color-primary)";
                e.target.style.boxShadow = `0 0 0 2px var(--color-primary-background)`;
              }}
              onBlur={(e) => {
                e.target.style.borderColor = "var(--color-border)";
                e.target.style.boxShadow = "none";
              }}
            />
          </div>

          <div>
            <label style={labelStyles}>
              <MessageSquare className="h-4 w-4 inline mr-2" />
              Subject *
            </label>
            <select
              className="w-full p-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2"
              style={{
                backgroundColor: "var(--color-input)",
                borderColor: "var(--color-border)",
                color: "var(--color-card-foreground)",
              }}
              value={formData.subject}
              onChange={(e) => handleInputChange("subject", e.target.value)}
              onFocus={(e) => {
                e.target.style.borderColor = "var(--color-primary)";
                e.target.style.boxShadow = `0 0 0 2px var(--color-primary-background)`;
              }}
              onBlur={(e) => {
                e.target.style.borderColor = "var(--color-border)";
                e.target.style.boxShadow = "none";
              }}
              required
            >
              <option value="">Select a subject</option>
              <option value="partnership">Partnership Opportunities</option>
              <option value="funding">Funding & Support</option>
              <option value="research">Research Collaboration</option>
              <option value="data">Data Contribution</option>
              <option value="media">Media & Press</option>
              <option value="general">General Inquiry</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label style={labelStyles}>Message *</label>
            <textarea
              className="w-full p-3 rounded-lg border transition-all duration-200 focus:outline-none focus:ring-2 min-h-[120px] resize-vertical"
              style={{
                backgroundColor: "var(--color-input)",
                borderColor: "var(--color-border)",
                color: "var(--color-card-foreground)",
              }}
              value={formData.message}
              onChange={(e) => handleInputChange("message", e.target.value)}
              placeholder="Tell us about your interest in TAIFA-FIALA and how we might work together..."
              rows={5}
              onFocus={(e) => {
                e.target.style.borderColor = "var(--color-primary)";
                e.target.style.boxShadow = `0 0 0 2px var(--color-primary-background)`;
              }}
              onBlur={(e) => {
                e.target.style.borderColor = "var(--color-border)";
                e.target.style.boxShadow = "none";
              }}
              required
            />
          </div>

          {submitStatus === "error" && (
            <div 
              className="p-4 border rounded-lg"
              style={{
                backgroundColor: "var(--color-destructive-background)",
                borderColor: "var(--color-destructive)",
              }}
            >
              <p 
                className="text-sm font-medium"
                style={{ color: "var(--color-destructive)" }}
              >
                There was an error sending your message. Please try again or
                contact us directly.
              </p>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 font-semibold transition-all duration-200 hover:shadow-lg"
              style={{
                backgroundColor: "var(--color-primary)",
                color: "var(--color-primary-foreground)",
              }}
              onMouseEnter={(e) => {
                const target = e.target as HTMLButtonElement;
                target.style.backgroundColor = "var(--color-primary-hover)";
              }}
              onMouseLeave={(e) => {
                const target = e.target as HTMLButtonElement;
                target.style.backgroundColor = "var(--color-primary)";
              }}
            >
              {isSubmitting ? (
                <>
                  <div 
                    className="animate-spin rounded-full h-4 w-4 border-b-2 mr-2"
                    style={{ borderColor: "var(--color-primary-foreground)" }}
                  ></div>
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
              className="font-semibold transition-all duration-200 hover:shadow-md"
              style={{
                backgroundColor: "var(--color-secondary)",
                color: "var(--color-secondary-foreground)",
                borderColor: "var(--color-secondary)",
              }}
              onMouseEnter={(e) => {
                const target = e.target as HTMLButtonElement;
                target.style.backgroundColor = "var(--color-secondary-hover)";
              }}
              onMouseLeave={(e) => {
                const target = e.target as HTMLButtonElement;
                target.style.backgroundColor = "var(--color-secondary)";
              }}
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
            <p 
              className="text-sm"
              style={{ color: "var(--color-muted-foreground)" }}
            >
              By submitting this form, you agree to our privacy policy and terms
              of service.
            </p>
          </div>
        </form>

        {/* Alternative Contact Methods */}
        <div 
          className="mt-12 pt-8 border-t"
          style={{ borderColor: "var(--color-border)" }}
        >
          <div className="text-center mb-6">
            <h4 
              className="text-lg font-semibold mb-2"
              style={{ color: "var(--color-card-foreground)" }}
            >
              Other Ways to Reach Us
            </h4>
            <p 
              className="text-sm"
              style={{ color: "var(--color-muted-foreground)" }}
            >
              Prefer direct contact? Here are additional ways to get in touch.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div 
              className="text-center p-6 rounded-lg border transition-all duration-200 hover:shadow-md"
              style={{
                backgroundColor: "var(--color-primary-background)",
                borderColor: "var(--color-primary)",
              }}
            >
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3"
                style={{
                  backgroundColor: "var(--color-primary)",
                  color: "var(--color-primary-foreground)",
                }}
              >
                <Mail className="h-6 w-6" />
              </div>
              <h5 
                className="font-semibold mb-1"
                style={{ color: "var(--color-primary)" }}
              >
                Email
              </h5>
              <p 
                className="text-sm font-medium"
                style={{ color: "var(--color-card-foreground)" }}
              >
                contact@taifa-fiala.org
              </p>
            </div>
            <div 
              className="text-center p-6 rounded-lg border transition-all duration-200 hover:shadow-md"
              style={{
                backgroundColor: "var(--color-info-background)",
                borderColor: "var(--color-info)",
              }}
            >
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3"
                style={{
                  backgroundColor: "var(--color-info)",
                  color: "var(--color-info-foreground)",
                }}
              >
                <MessageSquare className="h-6 w-6" />
              </div>
              <h5 
                className="font-semibold mb-1"
                style={{ color: "var(--color-info)" }}
              >
                Response Time
              </h5>
              <p 
                className="text-sm font-medium"
                style={{ color: "var(--color-card-foreground)" }}
              >
                24-48 hours
              </p>
            </div>
          </div>
        </div>
    </Card>
  );
}
