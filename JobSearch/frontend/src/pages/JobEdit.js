import { useState, useEffect, useContext } from "react";		

import { AuthContext } from "../context/AuthContext";
import { useParams, useNavigate, Navigate } from "react-router-dom";		
import { Button, Container } from "react-bootstrap";
import { Link } from "react-router-dom";

import { useQuery } from "@tanstack/react-query";		
import { API } from "../constants";		
import { Form } from "react-bootstrap";



export default function JobEdit() {

    const navigate = useNavigate();

    const { user, token } = useContext(AuthContext);

    const { id } = useParams(); 

    const [formData, setFormData] = useState({

      title: "",
      salary: "",
      description: "",
      location: "",
      latitude: null,  
      longitude: null,
      expiration: "",
      requirements: "",
      company: "",
      job_type: "FT",
   
    });

    
    const { isLoading, data, error } = useQuery({
      queryKey: ["jobs", id],
      queryFn: async () => {
        const response = await fetch(`${API}jobs/${id}/`);
        return await response.json();
      },
    });


    useEffect(() => {
      if (data) {
        setFormData({
          title: data.title || "",
          salary: data.salary || "",
          description: data.description  || "",
          location: data.location || "",
          latitude: data.latitude || "",  
          longitude: data.longitude || "",
          expiration: data.expiration|| "",
          requirements: data.requirements || "",
          company: data.company || "",
          job_type: data.job_type === "Full-time" ? "FT": data.job_type === "Part-time" ? "PT" : "FT", 
        });
      }
    }, [data]);
    
    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

  
    const handleChange = (e) => {
      const { name, value } = e.target;
      setFormData((prev) => ({
        ...prev, [name]: value,
      }));
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
  
      try {

        const response = await fetch(`${API}jobs/${data.id}/`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            ...formData,
            salary: parseFloat(formData.salary),
            company: user.modelId,
            }) 
        });
      
        if (!response.ok) throw new Error("Failed to submit job");
    
            const result = await response.json();
            alert("Job updated successfully!");
            navigate("/myjobs");

      } 
        catch (error) {
            alert("Error posting job:" + error.message);
      }
    };

  return (
    <Container className="mt-5">
      <h3>Update Job Details</h3>
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

        <Form.Group className="mb-3" controlId="formCompany">
          <Form.Label>Company</Form.Label>
          <Form.Control
            type="text"
            name="company"
            value={formData.company}
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

        <Form.Group className="mb-3" controlId="formLocation">
          <Form.Label>Location</Form.Label>
          <Form.Control
            type="text"
            name="location"
            value={formData.location}
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
        <Link to={`/myjobs`}>
          <Button variant="outline-success" size="sm">Cancel</Button> 
        </Link>
        <Button variant="primary" type="submit" className="w-100">
          Update Job
        </Button>
      </Form>
    </Container>
  );
}


