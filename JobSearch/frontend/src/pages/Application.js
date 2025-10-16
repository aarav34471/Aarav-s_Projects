// src/components/Application.js
import React, { useRef, useState, useEffect } from "react";
import { Form, Button, Container } from "react-bootstrap";
import { API } from "../constants";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useParams } from "react-router-dom";

function CreateApplicationForm() {
  const { user, token } = useContext(AuthContext);
  const { id } = useParams();
  
  const [formData, setFormData] = useState({
    cover_letter: null,
    cv:           null,
  });
  //use ref for files
  const coverRef = useRef(null);
  const cvRef    = useRef(null);
  //update data and files
  const handleChange = (e) => {
    const { name, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files[0] || null,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.cover_letter || !formData.cv) {
      return alert("Please upload both a cover letter and a CV.");
    }

    try {
      //Form Data to handle 
      const payload = new FormData();
      payload.append("graduate", user.modelId);
      payload.append("job", id);
      payload.append("cover_letter", formData.cover_letter);
      payload.append("cv",  formData.cv);
      payload.append("status", "APPLIED");
      
      const response = await fetch(`${API}applications/`, {
        method:  "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: payload,
      });


      if (!response.ok) {
        //use for debugging if error catch error gets triggered
        const errJson = await response.json();
        console.error("Validation errors:", errJson);
        throw new Error(errJson);
      }
      // makes sure applicaiton submitted then give alert
      const result = await response.json();
      alert("Application submitted successfully!");

      setFormData({ cover_letter: null, cv: null });
      coverRef.current.value = "";
      cvRef.current.value  = "";
    } catch (error) {
      alert("Error submitting application");
    }
  };

  return (
    <Container className="mt-5">
      <h3>Apply for Job #{id}</h3>
      <Form onSubmit={handleSubmit} className="mt-4">
        <Form.Group className="mb-3" controlId="formCoverLetter">
          <Form.Label>Cover Letter (PDF/DOC)</Form.Label>
          <Form.Control
            type="file"
            name="cover_letter"
            ref={coverRef}
            accept=".pdf,.doc,.docx"
            onChange={handleChange}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="formCV">
          <Form.Label>CV / Resume (PDF/DOC)</Form.Label>
          <Form.Control
            type="file"
            name="cv"
            ref={cvRef}
            accept=".pdf,.doc,.docx"
            onChange={handleChange}
            required
          />
        </Form.Group>

        <Button variant="primary" type="submit" className="w-100">
          Submit Application
        </Button>
      </Form>
    </Container>
  );
}

export default CreateApplicationForm;
