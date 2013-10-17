#!/usr/bin/perl -w

use strict;
use CGI;
use warnings;

my $proceed = 0;

my $ldap_host = "127.0.0.1";
my $ldap_port = "389";
my $admin_bind = "cn=admin,dc=example,dc=com";
my $admin_password = "password";
my $base_dn = "ou=People,dc=example,dc=com";

sub remove_white_spaces {
        $_ = shift;
        # remove leading spaces
        s/^\s+//;
        # remove ending spaces
        s/\s+$//;
        return $_;
}


my $q = CGI->new;
print $q->header;

print $q->start_html(
        -head => $q->meta({
        	-http_equiv => 'Content-Type',
			-content    => 'text/html; charset=UTF-8'
        }),
        -title => 'Change your LDAP password',
		-style=>{'src'=>'/css/ldap.css'});


my $username= $q->param('username') || '';
$username = remove_white_spaces($username);

my $oldPassword = $q->param('oldPassword') || '';
$oldPassword = remove_white_spaces($oldPassword);

my $newPassword = $q->param('newPassword') || '';
$newPassword = remove_white_spaces($newPassword);

my $newPassword2 = $q->param('newPassword2') || '';
$newPassword2 = remove_white_spaces($newPassword2);

if ($q->param) {
        $proceed = 1; 
#       print $q->Dump;
        $q->delete_all;
}

print $q->start_div({-id=>"container"}) ."\n";
print $q->h2("Change your password") . "\n";

print $q->start_ul . "\n";
print $q->li("Your new password must be at least 8 characters long, contains at least two letters (one upper and one lower case), and one digit.") . "\n";
print $q->end_ul . "\n";
print $q->start_form;

# print $q->start_table . "\n";
print $q->start_table({ -style  => 'width: 400px; margin: 0 auto;'}) . "\n";
print $q->start_Tr;
print $q->th("Username:");
print $q->start_td;
print $q->textfield(
        -name   => 'username',
        -type   => 'text',
        -size   => 20
);
print $q->end_td;
print $q->end_Tr . "\n";

print $q->start_Tr;
print $q->th("Old password:");
print $q->td([$q->password_field(-name=>'oldPassword', -autocomplete=>'off')]);
print $q->end_Tr . "\n";

print $q->start_Tr;
print $q->th("New password:");
print $q->td([$q->password_field(-name=>'newPassword', -autocomplete=>'off')]);
print $q->end_Tr . "\n";

print $q->start_Tr;
print $q->th("New password (confirm):");
print $q->td([$q->password_field(-name=>'newPassword2', -autocomplete=>'off')]);
print $q->end_Tr . "\n";

print $q->start_Tr;
print $q->td({-colspan=>2},[$q->submit('submit','Change password')]);
print $q->end_Tr . "\n";

print $q->end_table;
print $q->end_form . "\n";
print $q->div({-class=>"msg"});

if ($proceed) {
	my $flag = 0;
	if ( ($username && $oldPassword && $newPassword) && ($newPassword eq $newPassword2) && (length($newPassword) > 7) && ($newPassword =~ /\d/) && ($newPassword =~ m/\p{Uppercase}/) && ($newPassword =~ m/\p{Lowercase}/) ) {

		use Net::LDAP;
		my $ldap_username = "uid=$username,$base_dn";

		my $ldap = Net::LDAP->new("$ldap_host:$ldap_port") or die "$@";
		my $mesg = $ldap->bind( "$ldap_username" , password => "$oldPassword" );
		$ldap->unbind();

		if ( $mesg->is_error ) {
			print $q->p({-id=>'red'},$mesg->error);
			print $q->p({"Password unchanged.") . "\n";
		} else {
			use Net::LDAP::Extension::SetPassword;

	       	$ldap = Net::LDAP->new("$ldap_host:$ldap_port") or die "$@";
			$mesg = $ldap->bind( "$admin_bind" , password => "$admin_password" );
			$mesg = $ldap->set_password(
				newpasswd => "$newPassword",
				user      => "$ldap_username"
			);
			if ( $mesg->is_error ) {
				print $q->p({-id=>'red'},$mesg->error);
				print $q->p("Password unchanged.") . "\n";
			} else {
				print $q->p({-id=>'green'},"Password changed.") . "\n";
			}
			$ldap->unbind();
		}
	} else {
		if (!$username) {
			print $q->p({-id=>'red'},"Username is empty! Password unchanged.") . "\n";
		} elsif ( !$oldPassword ) {
			print $q->p({-id=>'red'},"Password is empty! Password unchanged.") . "\n";
		} elsif ( !$newPassword ) {
			print $q->p({-id=>'red'},"New password is empty! Password unchanged.") . "\n";
		} elsif ( !$newPassword2 ) {
			print $q->p({-id=>'red'},"New password (confirm) is empty! Password unchanged.") . "\n";
		} elsif ( $newPassword ne $newPassword2  ) {
			print $q->p({-id=>'red'},"New password mismatch! Password unchanged.") . "\n";
		} else {
			print $q->p({-id=>'red'},"Your new password must be at least 8 characters long, contains at least two letters (one upper and one lower case), and one digit! Password unchanged.") . "\n";
		}
	}
}
        
print $q->end_div. "\n";;

print $q->end_html;

