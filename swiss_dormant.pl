#!/usr/bin/perl 
#
# Get Rich, Dump stuff from Swiss banks angelos karageorgiou angelos@unix.gr
# 
use HTML::Form;
use WWW::Mechanize;
use HTML::Parser ();
use Data::Dumper;
use HTML::TableExtract;

my $mech = WWW::Mechanize->new();
my $url='https://www.dormantaccounts.ch/narilo/';

# first into the page, click on Publications
$mech->get( $url );
$mech->form_number(2);
$mech->click();

my $html = $mech->content();
dump_table($html);

my $cont=1;
while ($cont) {
    print "-" x 80 ."\n";
    $cont=0;
    my $form=$mech->form_number(2);
    my $saved_input=undef;
    foreach $input ($form->inputs) {
        if ($input->value eq 'Next') {
            $saved_input=$input;
            $cont=1;
        }
    }
    # just in case
    $mech->click_button( input => $saved_input);
    dump_table($mech->content());
}

sub dump_table () {
 my $html=shift;
 $te = HTML::TableExtract->new( );
 $te->parse($html);

 # Examine all matching tables
 foreach $ts ($te->tables) {
   next if $ts->coords == "0,0";
   foreach $row ($ts->rows) {
        foreach $col (@$row) {
            $col=~s/[\s][\s]*/ /g;
            print "'$col' ;";
        }
    print "\n";
   }
 }
}
