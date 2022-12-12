import React, {useState } from 'react';
import JobCard from './Components/JobCard/JobCard';
import Navbar from './Components/Navbar/Navbar';
import { AppContainer, Main } from './styles/app';
import { data } from "./Services/Data/data";


const App:React.FC = () => {
  const [search,setSearch]=useState('');
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>)=>{
    setSearch(e.target.value);
  }
  const handleClickFilter = (e:React.MouseEvent<HTMLDivElement, MouseEvent>)=>{
    const value = e.target as HTMLElement;
    setSearch(value.innerText);
  }
  return (
  <Main>
      <Navbar change={handleChange} clickFilter={handleClickFilter}/>
      <AppContainer>
        {
          data.filter((candidate)=>(
            search.toLocaleLowerCase()===''?
            candidate:
            candidate.job_title.toLocaleLowerCase().includes(search.toLocaleLowerCase())||
            candidate.job_tags.includes(search)
          )).map((candidate) => (
            <JobCard key={candidate.logo} data={candidate}  />
          ))}
          
      </AppContainer>
  </Main>
  )
}

export default App;