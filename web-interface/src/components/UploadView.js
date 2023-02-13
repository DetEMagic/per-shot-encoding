
import Container from 'react-bootstrap/Container'
import JobInput from './UploadComponents/JobInput';

function UploadView() {
    return (
        <div className="App">
            <Container>
                <h1 style={{ marginTop: "10vh" }}>Schedule Job</h1>
                <JobInput/>
            </Container>
        </div>
    );
}

export default UploadView;
