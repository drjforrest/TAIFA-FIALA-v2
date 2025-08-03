"use client";

import { useState } from "react";
import { Button, Card } from "@/components/ui";
import {
  ArrowLeft,
  Upload,
  Plus,
  X,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import Link from "next/link";
import { Section1Text } from "@/components/ui/adaptive-text";

interface InnovationFormData {
  title: string;
  description: string;
  innovationType: string;
  country: string;
  creationDate: string;
  organization: string;
  website: string;
  teamSize: number;
  tags: string[];
  impact: string;
  problemSolved: string;
  solution: string;
  techStack: string[];
  fundingAmount: number;
  fundingCurrency: string;
  evidenceFiles: File[];
  contactEmail: string;
  contactName: string;
}

const innovationTypes = [
  "HealthTech",
  "AgriTech",
  "FinTech",
  "EdTech",
  "CleanTech",
  "Logistics",
  "E-Government",
  "Media & Entertainment",
  "Security",
  "Other",
];

const countries = [
  "Algeria",
  "Angola",
  "Benin",
  "Botswana",
  "Burkina Faso",
  "Burundi",
  "Cameroon",
  "Cape Verde",
  "Central African Republic",
  "Chad",
  "Comoros",
  "Congo",
  "Democratic Republic of Congo",
  "Djibouti",
  "Egypt",
  "Equatorial Guinea",
  "Eritrea",
  "Eswatini",
  "Ethiopia",
  "Gabon",
  "Gambia",
  "Ghana",
  "Guinea",
  "Guinea-Bissau",
  "Ivory Coast",
  "Kenya",
  "Lesotho",
  "Liberia",
  "Libya",
  "Madagascar",
  "Malawi",
  "Mali",
  "Mauritania",
  "Mauritius",
  "Morocco",
  "Mozambique",
  "Namibia",
  "Niger",
  "Nigeria",
  "Rwanda",
  "Sao Tome and Principe",
  "Senegal",
  "Seychelles",
  "Sierra Leone",
  "Somalia",
  "South Africa",
  "South Sudan",
  "Sudan",
  "Tanzania",
  "Togo",
  "Tunisia",
  "Uganda",
  "Zambia",
  "Zimbabwe",
];

const currencies = [
  "USD",
  "EUR",
  "ZAR",
  "NGN",
  "KES",
  "GHS",
  "EGP",
  "MAD",
  "TND",
  "Other",
];

export default function SubmitInnovationPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<InnovationFormData>({
    title: "",
    description: "",
    innovationType: "",
    country: "",
    creationDate: "",
    organization: "",
    website: "",
    teamSize: 1,
    tags: [],
    impact: "",
    problemSolved: "",
    solution: "",
    techStack: [],
    fundingAmount: 0,
    fundingCurrency: "USD",
    evidenceFiles: [],
    contactEmail: "",
    contactName: "",
  });

  const [newTag, setNewTag] = useState("");
  const [newTech, setNewTech] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<
    "idle" | "success" | "error"
  >("idle");

  const handleInputChange = (field: keyof InnovationFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      handleInputChange("tags", [...formData.tags, newTag.trim()]);
      setNewTag("");
    }
  };

  const removeTag = (tagToRemove: string) => {
    handleInputChange(
      "tags",
      formData.tags.filter((tag) => tag !== tagToRemove),
    );
  };

  const addTech = () => {
    if (newTech.trim() && !formData.techStack.includes(newTech.trim())) {
      handleInputChange("techStack", [...formData.techStack, newTech.trim()]);
      setNewTech("");
    }
  };

  const removeTech = (techToRemove: string) => {
    handleInputChange(
      "techStack",
      formData.techStack.filter((tech) => tech !== techToRemove),
    );
  };

  const handleFileUpload = (files: FileList | null) => {
    if (files) {
      const newFiles = Array.from(files);
      handleInputChange("evidenceFiles", [
        ...formData.evidenceFiles,
        ...newFiles,
      ]);
    }
  };

  const removeFile = (fileToRemove: File) => {
    handleInputChange(
      "evidenceFiles",
      formData.evidenceFiles.filter((file) => file !== fileToRemove),
    );
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));
      setSubmitStatus("success");
    } catch (error) {
      setSubmitStatus("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => setCurrentStep((prev) => Math.min(prev + 1, 4));
  const prevStep = () => setCurrentStep((prev) => Math.max(prev - 1, 1));

  if (submitStatus === "success") {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: "var(--color-background)" }}
      >
        <Card
          className="max-w-md text-center"
          style={{ backgroundColor: "var(--color-card)" }}
        >
          <CheckCircle
            className="h-16 w-16 mx-auto mb-4"
            style={{ color: "var(--color-success)" }}
          />
          <h2
            className="text-2xl font-bold mb-4"
            style={{ color: "var(--color-card-foreground)" }}
          >
            Innovation Submitted Successfully!
          </h2>
          <p
            className="mb-6"
            style={{ color: "var(--color-muted-foreground)" }}
          >
            Thank you for contributing to Africa's AI innovation archive. We'll
            review your submission and notify you of the verification status.
          </p>
          <div className="space-y-3">
            <Link href="/innovations">
              <Button className="w-full">Explore Other Innovations</Button>
            </Link>
            <Link href="/submit">
              <Button variant="outline" className="w-full">
                Submit Another Innovation
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  const inputStyles = {
    width: "100%",
    padding: "var(--spacing-md)",
    borderRadius: "var(--radius-md)",
    border: "1px solid var(--color-border)",
    backgroundColor: "var(--color-input)",
    color: "var(--color-foreground)",
    fontSize: "1rem",
  };

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--color-background)" }}
    >
      {/* Header */}
      <div
        style={{
          backgroundColor: "var(--color-background-section-1)",
          borderBottom: "1px solid var(--color-border)",
        }}
      >
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Link href="/innovations" className="mr-4">
                <Button
                  variant="ghost"
                  size="sm"
                  style={{ color: "var(--color-text-section-1)" }}
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Innovations
                </Button>
              </Link>
              <div>
                <Section1Text as="h1" className="text-2xl font-bold">
                  Submit Your Innovation
                </Section1Text>
                <Section1Text as="p" variant="paragraph">
                  Share your AI innovation with the African tech community
                </Section1Text>
              </div>
            </div>
            <Section1Text as="div" variant="paragraph" className="text-sm">
              Step {currentStep} of 4
            </Section1Text>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div
            className="h-2 rounded-full"
            style={{ backgroundColor: "var(--color-border)" }}
          >
            <div
              className="h-2 rounded-full transition-all duration-300"
              style={{
                backgroundColor: "var(--color-primary)",
                width: `${(currentStep / 4) * 100}%`,
              }}
            />
          </div>
        </div>

        <Card>
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div>
              <h2
                className="text-xl font-semibold mb-6"
                style={{ color: "var(--color-card-foreground)" }}
              >
                Basic Information
              </h2>
              <div className="space-y-6">
                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    Innovation Title *
                  </label>
                  <input
                    type="text"
                    style={inputStyles}
                    value={formData.title}
                    onChange={(e) => handleInputChange("title", e.target.value)}
                    placeholder="Enter your innovation title"
                  />
                </div>

                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-card-foreground)" }}
                  >
                    Description *
                  </label>
                  <textarea
                    style={{ ...inputStyles, minHeight: "120px" }}
                    value={formData.description}
                    onChange={(e) =>
                      handleInputChange("description", e.target.value)
                    }
                    placeholder="Describe your innovation and its impact"
                    rows={4}
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-card-foreground)" }}
                    >
                      Innovation Type *
                    </label>
                    <select
                      style={inputStyles}
                      value={formData.innovationType}
                      onChange={(e) =>
                        handleInputChange("innovationType", e.target.value)
                      }
                    >
                      <option value="">Select type</option>
                      {innovationTypes.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-card-foreground)" }}
                    >
                      Country *
                    </label>
                    <select
                      style={inputStyles}
                      value={formData.country}
                      onChange={(e) =>
                        handleInputChange("country", e.target.value)
                      }
                    >
                      <option value="">Select country</option>
                      {countries.map((country) => (
                        <option key={country} value={country}>
                          {country}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-card-foreground)" }}
                    >
                      Creation Date
                    </label>
                    <input
                      type="date"
                      style={inputStyles}
                      value={formData.creationDate}
                      onChange={(e) =>
                        handleInputChange("creationDate", e.target.value)
                      }
                    />
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Team Size
                    </label>
                    <input
                      type="number"
                      style={inputStyles}
                      value={formData.teamSize}
                      onChange={(e) =>
                        handleInputChange(
                          "teamSize",
                          parseInt(e.target.value) || 1,
                        )
                      }
                      min="1"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Organization & Contact */}
          {currentStep === 2 && (
            <div>
              <h2
                className="text-xl font-semibold mb-6"
                style={{ color: "var(--color-foreground)" }}
              >
                Organization & Contact
              </h2>
              <div className="space-y-6">
                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Organization Name
                  </label>
                  <input
                    type="text"
                    style={inputStyles}
                    value={formData.organization}
                    onChange={(e) =>
                      handleInputChange("organization", e.target.value)
                    }
                    placeholder="Your organization or company name"
                  />
                </div>

                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Website
                  </label>
                  <input
                    type="url"
                    style={inputStyles}
                    value={formData.website}
                    onChange={(e) =>
                      handleInputChange("website", e.target.value)
                    }
                    placeholder="https://your-website.com"
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Contact Name *
                    </label>
                    <input
                      type="text"
                      style={inputStyles}
                      value={formData.contactName}
                      onChange={(e) =>
                        handleInputChange("contactName", e.target.value)
                      }
                      placeholder="Your full name"
                    />
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Contact Email *
                    </label>
                    <input
                      type="email"
                      style={inputStyles}
                      value={formData.contactEmail}
                      onChange={(e) =>
                        handleInputChange("contactEmail", e.target.value)
                      }
                      placeholder="your.email@example.com"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Technical Details */}
          {currentStep === 3 && (
            <div>
              <h2
                className="text-xl font-semibold mb-6"
                style={{ color: "var(--color-foreground)" }}
              >
                Technical Details
              </h2>
              <div className="space-y-6">
                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Problem Solved
                  </label>
                  <textarea
                    style={{ ...inputStyles, minHeight: "100px" }}
                    value={formData.problemSolved}
                    onChange={(e) =>
                      handleInputChange("problemSolved", e.target.value)
                    }
                    placeholder="What specific problem does your innovation address?"
                    rows={3}
                  />
                </div>

                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Solution Approach
                  </label>
                  <textarea
                    style={{ ...inputStyles, minHeight: "100px" }}
                    value={formData.solution}
                    onChange={(e) =>
                      handleInputChange("solution", e.target.value)
                    }
                    placeholder="How does your innovation solve this problem?"
                    rows={3}
                  />
                </div>

                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Impact & Results
                  </label>
                  <textarea
                    style={{ ...inputStyles, minHeight: "100px" }}
                    value={formData.impact}
                    onChange={(e) =>
                      handleInputChange("impact", e.target.value)
                    }
                    placeholder="What impact has your innovation achieved? Include metrics if available."
                    rows={3}
                  />
                </div>

                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Technology Stack
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      style={{ ...inputStyles, flex: 1 }}
                      value={newTech}
                      onChange={(e) => setNewTech(e.target.value)}
                      placeholder="Add technology (e.g., Python, TensorFlow)"
                      onKeyPress={(e) =>
                        e.key === "Enter" && (e.preventDefault(), addTech())
                      }
                    />
                    <Button onClick={addTech} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.techStack.map((tech, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm"
                        style={{
                          backgroundColor: "var(--color-accent)",
                          color: "var(--color-accent-foreground)",
                        }}
                      >
                        {tech}
                        <button
                          onClick={() => removeTech(tech)}
                          className="ml-2 hover:opacity-70"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Tags
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      style={{ ...inputStyles, flex: 1 }}
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      placeholder="Add tag (e.g., Machine Learning, NLP)"
                      onKeyPress={(e) =>
                        e.key === "Enter" && (e.preventDefault(), addTag())
                      }
                    />
                    <Button onClick={addTag} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm"
                        style={{
                          backgroundColor: "var(--color-secondary)",
                          color: "var(--color-secondary-foreground)",
                        }}
                      >
                        {tag}
                        <button
                          onClick={() => removeTag(tag)}
                          className="ml-2 hover:opacity-70"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Funding & Evidence */}
          {currentStep === 4 && (
            <div>
              <h2
                className="text-xl font-semibold mb-6"
                style={{ color: "var(--color-foreground)" }}
              >
                Funding & Evidence
              </h2>
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Funding Amount (Optional)
                    </label>
                    <input
                      type="number"
                      style={inputStyles}
                      value={formData.fundingAmount}
                      onChange={(e) =>
                        handleInputChange(
                          "fundingAmount",
                          parseFloat(e.target.value) || 0,
                        )
                      }
                      placeholder="0"
                      min="0"
                    />
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: "var(--color-foreground)" }}
                    >
                      Currency
                    </label>
                    <select
                      style={inputStyles}
                      value={formData.fundingCurrency}
                      onChange={(e) =>
                        handleInputChange("fundingCurrency", e.target.value)
                      }
                    >
                      {currencies.map((currency) => (
                        <option key={currency} value={currency}>
                          {currency}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label
                    className="block text-sm font-medium mb-2"
                    style={{ color: "var(--color-foreground)" }}
                  >
                    Supporting Evidence
                  </label>
                  <div
                    className="border-2 border-dashed rounded-lg p-6 text-center"
                    style={{ borderColor: "var(--color-border)" }}
                  >
                    <Upload
                      className="h-8 w-8 mx-auto mb-2"
                      style={{ color: "var(--color-muted-foreground)" }}
                    />
                    <p
                      style={{ color: "var(--color-muted-foreground)" }}
                      className="mb-2"
                    >
                      Upload documents, images, or videos that demonstrate your
                      innovation
                    </p>
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.mp4,.mov"
                      onChange={(e) => handleFileUpload(e.target.files)}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload">
                      <Button variant="outline" size="sm">
                        Choose Files
                      </Button>
                    </label>
                  </div>

                  {formData.evidenceFiles.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {formData.evidenceFiles.map((file, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 rounded-lg"
                          style={{ backgroundColor: "var(--color-muted)" }}
                        >
                          <span style={{ color: "var(--color-foreground)" }}>
                            {file.name}
                          </span>
                          <button
                            onClick={() => removeFile(file)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div
                  className="p-4 rounded-lg"
                  style={{ backgroundColor: "var(--color-accent)" }}
                >
                  <div className="flex items-start">
                    <AlertCircle
                      className="h-5 w-5 mt-0.5 mr-3"
                      style={{ color: "var(--color-accent-foreground)" }}
                    />
                    <div>
                      <h4
                        className="font-medium"
                        style={{ color: "var(--color-accent-foreground)" }}
                      >
                        Verification Process
                      </h4>
                      <p
                        className="text-sm mt-1"
                        style={{ color: "var(--color-accent-foreground)" }}
                      >
                        Your submission will go through our community
                        verification process. Providing supporting evidence
                        increases the likelihood of verification.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div
            className="flex justify-between mt-8 pt-6"
            style={{ borderTop: "1px solid var(--color-border)" }}
          >
            <div>
              {currentStep > 1 && (
                <Button variant="outline" onClick={prevStep}>
                  Previous
                </Button>
              )}
            </div>
            <div>
              {currentStep < 4 ? (
                <Button onClick={nextStep}>Next</Button>
              ) : (
                <Button onClick={handleSubmit} disabled={isSubmitting}>
                  {isSubmitting ? "Submitting..." : "Submit Innovation"}
                </Button>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
