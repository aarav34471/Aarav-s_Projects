
import { Container, Nav, Navbar } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from "react-router-dom";


function MyNav() {


  const { user, logout } = useContext(AuthContext);


  const navigate = useNavigate()


  const handleClick = () => {
    logout()            // clears user, token, axios header, localStorage
    navigate('/login')  // send them back to login page
  }


  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container fluid>
        <Navbar.Brand as={Link} to="/">ReadyJobs</Navbar.Brand>
        <Navbar.Toggle aria-controls="main-navbar" />
        <Navbar.Collapse id="main-navbar">

          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">Home</Nav.Link>
            <Nav.Link as={Link} to="/jobs">Jobs</Nav.Link>
            
            {user?.account_type === 'employer' && (
              <>
                <Nav.Link as={Link} to="/jobs/create">Post Job</Nav.Link>
                <Nav.Link as={Link} to="/myjobs">My Jobs</Nav.Link>
                <Nav.Link as={Link} to="/viewapplications">Applications</Nav.Link>
              </>
            )}
            {user?.account_type === 'graduate' && (
              <>
                <Nav.Link as={Link} to="/bookmarks">Bookmarks</Nav.Link>
                <Nav.Link as={Link} to="/myapplications">My Applications</Nav.Link>
              </>
            )}
            <Nav.Link as={Link} to="/resources">Resources</Nav.Link>
          </Nav>
          


          <Nav className="ms-auto">
            {user ? (
              <Nav.Link onClick={handleClick}>
                Log out
              </Nav.Link>
            ) : (
              <Nav.Link as={Link} to="/login">
                Log In
              </Nav.Link>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}



export default MyNav;
