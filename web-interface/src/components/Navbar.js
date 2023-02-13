
import React, { Component } from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap'

class Navigation extends Component {
    render() {
        return (
            <Navbar bg="light" sticky="top">
                <Container fluid>
                    <LinkContainer to="/">
                        <Navbar.Brand>Krosus</Navbar.Brand>
                    </LinkContainer>
                    <Navbar.Toggle aria-controls="basic-navbar-nav" />
                    <Navbar.Collapse id="basic-navbar-nav">
                        <Nav className="me-auto">
                            <LinkContainer to="/">
                                <Nav.Link>Upload</Nav.Link>
                            </LinkContainer>
                            <LinkContainer to="/jobs">
                                <Nav.Link>Jobs</Nav.Link>
                            </LinkContainer>
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>
        );
    }
}

export default Navigation;
