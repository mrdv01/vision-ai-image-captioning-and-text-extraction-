import React, { useState } from "react";
import axios from "axios";
import { FiUploadCloud } from "react-icons/fi";
import { MdOutlineClosedCaption, MdTextSnippet } from "react-icons/md";
import { RiLoader4Line } from "react-icons/ri";

const UploadImage = () => {
  const [image, setImage] = useState(null);
  const [caption, setCaption] = useState("");
  const [extractedText, setExtractedText] = useState("");
  const [captionLoading, setCaptionLoading] = useState(false);
  const [textLoading, setTextLoading] = useState(false);
  const [captionError, setCaptionError] = useState("");
  const [textError, setTextError] = useState("");
  const [mode, setMode] = useState("light");

  const toggleMode = () => {
    setMode((prevMode) => (prevMode === "light" ? "dark" : "light"));
  };

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
    setCaption("");
    setExtractedText("");
    setCaptionError("");
    setTextError("");
  };

  const handleUpload = async (type) => {
    if (!image) {
      alert("Please select an image first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", image);

    if (type === "caption") {
      setCaptionLoading(true);
      setCaptionError("");
    } else {
      setTextLoading(true);
      setTextError("");
    }

    try {
      const endpoint = type === "caption" ? "caption" : "extract-text-auto";

      const response = await axios.post(
        `http://127.0.0.1:8000/${endpoint}/`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      if (type === "caption") {
        setCaption(response.data.caption || "No caption found.");
      } else {
        setExtractedText(response.data.text || "No text found.");
      }
    } catch (error) {
      console.error("Error processing image:", error);
      if (type === "caption") {
        setCaptionError(
          "⚠️ Unable to generate caption. Please try another image."
        );
      } else {
        setTextError(
          "⚠️ Unable to extract text. Ensure the image has clear text."
        );
      }
    } finally {
      if (type === "caption") setCaptionLoading(false);
      if (type === "extract-text") setTextLoading(false);
    }
  };

  return (
    <div
      className={`flex flex-col items-center ${
        mode === "dark" ? "bg-gray-900 text-white" : "bg-gray-100"
      } min-h-screen py-10 transition-all`}
    >
      <button
        onClick={toggleMode}
        className="absolute top-4 right-4 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition"
      >
        {mode === "light" ? "Dark Mode 🌙" : "Light Mode ☀️"}
      </button>

      <h1 className="text-3xl font-bold mb-6">
        Vision AI Image Captioning & Text Extraction
      </h1>

      <label className="flex flex-col items-center bg-white p-6 rounded-xl shadow-lg border-2 border-dashed cursor-pointer hover:bg-gray-50 transition">
        <FiUploadCloud size={50} className="text-gray-500" />
        <span className="mt-2 text-gray-600 font-semibold">
          Click to Upload Image
        </span>
        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleImageChange}
        />
      </label>

      {image && (
        <div className="mt-6 p-4 bg-white/70 shadow-lg rounded-lg backdrop-blur-md">
          <img
            src={URL.createObjectURL(image)}
            alt="Uploaded Preview"
            className="w-64 h-64 object-cover rounded-md shadow-lg"
          />
        </div>
      )}

      <div className="flex space-x-4 mt-6">
        <button
          className="px-5 py-3 flex items-center bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition"
          onClick={() => handleUpload("caption")}
          disabled={captionLoading}
        >
          {captionLoading ? (
            <RiLoader4Line className="animate-spin" />
          ) : (
            <MdOutlineClosedCaption size={20} className="mr-2" />
          )}
          {captionLoading ? "Processing..." : "Get Caption"}
        </button>

        <button
          className="px-5 py-3 flex items-center bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 transition"
          onClick={() => handleUpload("extract-text")}
          disabled={textLoading}
        >
          {textLoading ? (
            <RiLoader4Line className="animate-spin" />
          ) : (
            <MdTextSnippet size={20} className="mr-2" />
          )}
          {textLoading ? "Processing..." : "Extract Text"}
        </button>
      </div>

      {caption && (
        <div className="mt-6 p-6 bg-white shadow-lg rounded-lg w-3/4">
          <h2 className="font-bold text-lg">📝 Caption:</h2>
          <p className="text-gray-700">{caption}</p>
        </div>
      )}
      {captionError && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg w-3/4">
          {captionError}
        </div>
      )}

      {extractedText && (
        <div className="mt-6 p-6 bg-white shadow-lg rounded-lg w-3/4">
          <h2 className="font-bold text-lg">📜 Extracted Text:</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{extractedText}</p>
        </div>
      )}
      {textError && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg w-3/4">
          {textError}
        </div>
      )}
    </div>
  );
};

export default UploadImage;
