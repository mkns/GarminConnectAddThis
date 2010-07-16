#!/usr/bin/perl -w

use strict;
use CGI qw( :all );
use LWP::Simple;
use Data::Dumper;

print header();
my $garmin_url = "http://connect.garmin.com/activity/";

if ( !param() ) {
  show_form();
}
elsif( defined( param( "a" ) ) && length( param( "a" ) ) > 0 ) {
  addThis();
}
elsif ( param( "id" ) && param( "action" ) eq "confirm" ) {
  validate_id();
  confirm_details();
}
elsif ( param( "id" ) && param( "action" ) eq "write" ) {
  validate_id();
  write_data();
}

sub addThis {
  my $id = param( "a" );
  validate_id( $id );
  open( FILE, "data/$id/data.txt" ) or die $!;
  my $title = <FILE>;
  my $description = <FILE>;
  chomp( $title, $description );
  close( FILE );
  # print "title: $title\ndescription: $description\nid: $id\n";
  open( TEMPLATE, "template.html" ) or die $!;
  my $template = join( "", <TEMPLATE> );
  close( TEMPLATE );
  $template =~ s/__ID__/$id/g;
  $template =~ s/__TITLE__/$title/g;
  $template =~ s/__DESCRIPTION__/$description/g;
  print $template;
}

sub validate_id {
  my ( $id ) = @_;
  if ( !defined( $id ) ) {
    $id = param( "id" );
  }
  die unless defined( $id ) && $id =~ /^\d+$/;
}

sub confirm_details {
  my $id = param( "id" );
  my $response = get $garmin_url . $id;
  ( my $title ) = $response =~ /\<meta name="title" content="(.+?) \- .* \- Garmin Connect" \/\>/;
  param( "action", "write" );
  print join( "\n",
	      start_html( "Garmin Connect: AddThis" ),
	      start_multipart_form( -method => "post" ),
	      p( "Title: ", textfield( "title", $title ) ),
	      p( "Description: ", textfield( "description", "", 100 ) ),
	      filefield('uploaded_file'),
	      submit(),
	      hidden( "id", $id ),
	      hidden( "action", "write" ),
	      end_form(),
	      end_html(),
	    );
}

sub write_data {
  my $id = param( "id" );
  my $title = param( "title" );
  my $description = param( "description" );
  write_image();
  open( FILE, "> data/$id/data.txt" ) or die $!;
  print FILE $title, "\n", $description, "\n";
  close( FILE );
  print p( "<a href='http://www.facebook.com/share.php?u=http://kennyscott.com/GarminConnectAddThis/?a=$id'>Let's go to AddThis!</a>" );
}

sub write_image {
  my $id = param( "id" );
  mkdir "data/$id" or die "unable to mkdir: $!";
  open (OUTFILE,">> data/$id/map.png");
  my $fh = upload('uploaded_file');
  my $buffer;
  while ( my $bytesread = read( $fh, $buffer, 1024 ) ) {
    print OUTFILE $buffer;
  }
  close( OUTFILE );
}

sub show_form {
  print join( "\n",
	      start_html( "Garmin Connect: AddThis" ),
	      start_multipart_form( -method => "post" ),
	      p( "ID: ", textfield( "id" ) ),
	      hidden( "action", "confirm" ),
	      submit(),
	      end_form(),
	      end_html(),
	    );
}
