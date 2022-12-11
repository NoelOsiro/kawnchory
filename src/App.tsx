import React from 'react';
import JobCard from './Components/JobCard/JobCard';
import Navbar from './Components/Navbar/Navbar';
import { AppContainer, Main } from './styles/app';
import {data} from "./Services/Data/data";

 const App:React.FC = ()=> (
   <Main>
    <Navbar/> 
    <AppContainer>
      {
      data.map((candidate)=>(
        <JobCard data={candidate}/>
      ))}
    </AppContainer>
   
  </Main>
 )

 export default App;