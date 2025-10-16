
import { Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import MyNav from "./elements/Navbar";
import JobDetail from "./pages/JobDetail";
import Index from "./pages/Index";
import CreateJobForm from "./pages/CreateJob"
import SignUp from "./pages/SignUp";
import Login from "./pages/Login";
import Bookmarks from "./pages/Bookmarks";
import Logout from "./pages/Logout";
import { AuthContext } from "./context/AuthContext";
import { Navigate } from "react-router-dom";
import { useContext } from "react";
import { useState, useEffect } from "react";
import JobEdit from "./pages/JobEdit";
import EmployerJobView from "./pages/EmployerJobView";
import CreateApplicationForm from "./pages/Application";
import ApplicationView from "./pages/EmployerApplicationView";
import GraduateApplications from "./pages/GraduateApplicationView";
import Resource from "./pages/Resources";

function App() {

  const { user } = useContext(AuthContext);

  //get accountType whenever user changes
  const [accountType, setAccountType] = useState(null);
  useEffect(() => {
    setAccountType(user?.account_type ?? null);
  }, [user]);


  return (
    <>
          <MyNav />
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/jobs/" element={<Home />} />
            <Route path="/jobs/:id" element={<JobDetail />} />
            <Route path="/resources/" element={<Resource />} />

            
            <Route path="/jobs/create" element={ accountType==="employer" ? <CreateJobForm /> : <Navigate to="/" replace /> } />
            <Route path="/myjobs/" element={ accountType ==="employer" ? <EmployerJobView />: <Navigate to="/" replace /> } />
            <Route path="/myjobs/edit/:id" element={ accountType==="employer" ? <JobEdit />: <Navigate to="/" replace  /> } />

            <Route path="/application/:id" element={ accountType==="graduate" ? <CreateApplicationForm />: <Navigate to="/" replace  /> } />
            <Route path="/myapplications/" element={ accountType==="graduate" ? <GraduateApplications />: <Navigate to="/" replace  /> } />
            <Route path="/bookmarks/" element={ accountType==="graduate" ? <Bookmarks />: <Navigate to="/" replace  /> } />


            <Route path="/viewapplications/" element={ accountType==="employer" ? <ApplicationView />: <Navigate to="/" replace  /> } />


            <Route path="/logout" element={ user ? <Logout /> : <Navigate to="/login" replace /> } /> 
            <Route path="/login" element={ !user ? <Login /> : <Navigate to="/" replace /> } /> 
            <Route path="/signup" element={ !user ? <SignUp /> : <Navigate to="/" replace /> } /> 
          </Routes>
    </>

  );
}

export default App;
