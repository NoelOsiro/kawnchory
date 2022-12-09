import React from 'react';
import JobCard from './Components/JobCard/JobCard';
import Navbar from './Components/Navbar/Navbar';
import { AppContainer, Main } from './styles/app';

 const App:React.FC = ()=> (
   <Main>
    <Navbar/> 
    <AppContainer>
      <JobCard/>
    </AppContainer>
   
  </Main>
 )

 export default App;