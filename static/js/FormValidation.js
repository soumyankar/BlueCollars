function validate() {

   if( document.inputform.name.value == "" ) {
      alert( "Please provide Applicant's Name!" );
      document.inputform.name.focus() ;
      return false;
   }
   if( document.inputform.address.value == "" ) {
      alert( "Please provide Applicant's Address!" );
      document.inputform.address.focus() ;
      return false;
   }
   if( document.inputform.phone.value == "" ) {
      alert( "Please provide Applicant's Phone" );
   document.inputform.phone.focus() ;
   return false;
   }
   if( document.inputform.gender.value == "-1" ) {
   alert( "Please provide Applicant's Gender!" );
   return false;
}
return( true );
}
