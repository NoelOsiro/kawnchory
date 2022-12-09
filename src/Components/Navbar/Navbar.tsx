import React from 'react'
import {  NavShape } from './styles'
import Nav from '../../assets/images/nav.jpg'
import FilterBar from '../FilterBar/FilterBar'

const Navbar = () => {
  return (
    <NavShape>
      <img src={Nav} alt='' />
      <FilterBar/>
    </NavShape>
  )
}

export default Navbar