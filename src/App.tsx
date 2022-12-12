import React, { useContext, useState } from 'react';
import JobCard from './Components/JobCard/JobCard';
import Navbar from './Components/Navbar/Navbar';
import { AppContainer, Main } from './styles/app';
import { data } from "./Services/Data/data";


const App:React.FC = () => {
  const [search,setSearch]=useState('')
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>)=>{
    setSearch(e.target.value);
  }

  return (
  <Main>
      <Navbar change={handleChange} />
      <AppContainer>
        {
          data.filter((candidate)=>(
            search.toLocaleLowerCase()===''?
            candidate:
            candidate.job_title.toLocaleLowerCase().includes(search)
          )).map((candidate) => (
            <JobCard data={candidate} key={candidate.logo} />
          ))}
          
      </AppContainer>
  </Main>
  )
}

export default App;