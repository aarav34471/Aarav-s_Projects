import React, { useRef, useState, useEffect } from "react";
import { Form, Button, Container } from "react-bootstrap";

import { API } from "../constants";
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

function CreateJobForm() {

  const { user } = useContext(AuthContext);
    
  const [formData, setFormData] = useState({
    title: "",
    salary: "",
    description: "",
    location: "",
    latitude: null,  
    longitude: null,
    expiration: "",
    requirements: "",
    job_type: "PT",
    company: "",
   
    

  });

  const locRef = useRef(null);


  useEffect(() => {
    if (
      !window.google ||
      !window.google.maps ||
      !window.google.maps.places ||
      !locRef.current
    ) {
      return;
    }
    //Api for auto fill location and extract lat and long 
    const ac = new window.google.maps.places.Autocomplete(locRef.current, {
      types: ["geocode"],
    });
    ac.addListener("place_changed", () => {
      const place = ac.getPlace();
      if (!place.geometry) return;
      setFormData((f) => ({
        ...f,
        location:  place.formatted_address,
        latitude:  place.geometry.location.lat(),
        longitude: place.geometry.location.lng(),
      }));
    });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev, [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();


  try {
 

    const response = await fetch(`${API}jobs/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ...formData,
        salary: parseFloat(formData.salary),
        company: user.modelId,
        }) 
    });
  
    if (!response.ok) throw new Error("Failed to submit job");

        const result = await response.json();
        alert("Job posted successfully!");

    setFormData({
      title: "",
      salary: "",
      description: "",
      location: "",
      expiration: "",
      company: "",
      job_type: "PT",
      requirements: "",
    });
  } 
    catch (error) {
        alert("Error posting job:" + error.message);
  }
  };

  return (

    <Container className="mt-5">
      <h3>Create a Job Posting</h3>
      <Form onSubmit={handleSubmit} className="mt-4">
        <Form.Group className="mb-3" controlId="formTitle">
          <Form.Label>Job Title</Form.Label>
          <Form.Control
            type="text"
            name="title"
            placeholder="e.g., Software Engineer"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="formSalary">
            <Form.Label>Salary (£)</Form.Label>
                <Form.Control
                    type="number"
                    step="any" // 
                    name="salary"
                    value={formData.salary}
                    onChange={handleChange}
                    required
                />
            </Form.Group>
        
        <Form.Group className="mb-3" controlId="formDescription">
          <Form.Label>Description</Form.Label>
          <Form.Control
            as="textarea"
            name="description"
            rows={4}
            value={formData.description}
            onChange={handleChange}
            required
          />
        </Form.Group>


        <Form.Group className="mb-3" controlId="formExpiration">
            <Form.Label>Expiration Date</Form.Label>
                <Form.Control
                    type="date"
                    name="expiration"
                    value={formData.expiration}
                    onChange={handleChange}
                    required
                />
        </Form.Group>

        <Form.Group className="mb-3" controlId="formLocation">
          <Form.Label>Location</Form.Label>
          <Form.Control
            type="text"
            name="location"
            placeholder="Start typing address…"
            ref={locRef}                 
            value={formData.location}
            onChange={handleChange}
            required
          />
        </Form.Group>



        <Form.Group className="mb-3" controlId="formRequirements">
          <Form.Label>Requirements</Form.Label>
            <Form.Control
              as="textarea"
              name="requirements"
              rows={4}
              value={formData.requirements}
              onChange={handleChange}
              required
            />
        </Form.Group>

        <Form.Group className="mb-3" controlId="formJobType">
          <Form.Label>Job Type</Form.Label>
          <Form.Select
            name="job_type"
            value={formData.job_type}
            onChange={handleChange}
            required
          >
            <option value="PT">Part-time</option>
            <option value="FT">Full-time</option>
          </Form.Select>
        </Form.Group>

        <Button variant="primary" type="submit" className="w-100">
          Post Job
        </Button>
      </Form>
    </Container>
  );
}

export default CreateJobForm;
